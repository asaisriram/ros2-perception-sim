"""Test counter publisher and subscriber interaction."""

import os

from fake_sensors.counter_publisher import CounterPublisher
from fake_sensors.sensor_monitor import SensorMonitor
from fake_sensors.temperature_publisher import TemperaturePublisher

import pytest
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data, qos_profile_services_default
from sensor_msgs.msg import Temperature
from std_msgs.msg import Bool, Float32


@pytest.fixture(scope='session', autouse=True)
def set_ros_domain_id():
    """Set the ROS domain used by the test session."""
    os.environ['ROS_DOMAIN_ID'] = '77'
    yield


@pytest.fixture
def ros_context():
    """Initialize and shut down the ROS context for a test."""
    rclpy.init()
    yield
    rclpy.shutdown()


class SubscriberTestNode(Node):
    """Test node created for subscription."""

    def __init__(self, topic_name, msg_type, qos=10):
        """Initialize test node."""
        super().__init__('testnode_subscriber')
        self.topic_name = topic_name
        self.msg_type = msg_type
        self.msg_data = None
        self.test_subscriber_ = self.create_subscription(
            self.msg_type, self.topic_name,
            self.subscriber_testnode_callback, qos)

    def subscriber_testnode_callback(self, msg):
        """Record the received message data."""
        if self.msg_type == Temperature:
            self.msg_data = msg.temperature
        else:
            self.msg_data = msg.data


def test_counter_publisher_publishes(ros_context):
    """Verify the counter publisher delivers a message to a subscriber."""
    count = 5
    node_publisher = CounterPublisher()
    subscriber_testnode = SubscriberTestNode('/fake/counter', Float32)
    for _ in range(count):
        rclpy.spin_once(node_publisher, timeout_sec=0.2)
        rclpy.spin_once(subscriber_testnode, timeout_sec=0.2)
    received = subscriber_testnode.msg_data
    node_publisher.destroy_node()
    subscriber_testnode.destroy_node()
    assert received is not None


def test_temperature_publisher_publishes(ros_context):
    """Verify the temperature publisher delivers a message to a subscriber."""
    count = 5
    node_publisher = TemperaturePublisher()
    subscriber_testnode = SubscriberTestNode(
        '/fake/temperature', Temperature, qos_profile_sensor_data)
    for _ in range(count):
        rclpy.spin_once(node_publisher, timeout_sec=0.2)
        rclpy.spin_once(subscriber_testnode, timeout_sec=0.2)
    received = subscriber_testnode.msg_data
    node_publisher.destroy_node()
    subscriber_testnode.destroy_node()
    assert received is not None


def test_temperature_publisher_qos_profile(ros_context):
    """Verify the qos profile mismatch between subscriber and publisher."""
    count = 5
    node_publisher = TemperaturePublisher()
    subscriber_testnode = SubscriberTestNode(
        '/fake/temperature', Temperature, qos_profile_services_default)
    for _ in range(count):
        rclpy.spin_once(node_publisher, timeout_sec=0.2)
        rclpy.spin_once(subscriber_testnode, timeout_sec=0.2)
    received = subscriber_testnode.msg_data
    node_publisher.destroy_node()
    subscriber_testnode.destroy_node()
    assert received is None


def test_sensor_monitor_subscribes(ros_context):
    """Verify the monitor records data from both sensor topics."""
    count = 10
    counter_publisher = CounterPublisher()
    temperature_publisher = TemperaturePublisher()
    sensor_monitor = SensorMonitor()
    for _ in range(count):
        rclpy.spin_once(counter_publisher, timeout_sec=0.2)
        rclpy.spin_once(temperature_publisher, timeout_sec=0.2)
        rclpy.spin_once(sensor_monitor, timeout_sec=0.2)
    last_counter = sensor_monitor.last_counter
    last_temperature = sensor_monitor.last_temperature
    counter_publisher.destroy_node()
    temperature_publisher.destroy_node()
    sensor_monitor.destroy_node()
    assert last_counter is not None
    assert last_temperature is not None


@pytest.mark.parametrize('value1, value2, threshold, expected', [
    (10.0, 25.0, 55.0, False),   # 20+0.5*10=25.0 -> Plausible, under threshold
    (10.0, 25.8, 55.0, True),    # abs(25.0-25.6) > 0.5 -> PLAUSI_ERROR
    (42.5, 41.25, 40.0, True),   # 42.5 > 40.0 -> THRESHOLD_ERROR
])
def test_sensor_monitor_publishes(ros_context, value1, value2, threshold, expected):
    """Verify the sensor monitor publishes error states."""
    count = 5
    sensor_monitor = SensorMonitor()
    warning_subscriber = SubscriberTestNode('/status/warning', Bool)
    counter_msg = Float32()
    counter_msg.data = value1
    temperature_msg = Temperature()
    temperature_msg.temperature = value2
    sensor_monitor.threshold = threshold
    sensor_monitor.counter_callback(counter_msg)
    sensor_monitor.temperature_callback(temperature_msg)
    for _ in range(count):
        rclpy.spin_once(warning_subscriber, timeout_sec=0.2)
    warning_status = warning_subscriber.msg_data
    sensor_monitor.destroy_node()
    warning_subscriber.destroy_node()
    assert warning_status == expected

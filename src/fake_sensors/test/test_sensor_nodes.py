"""Test counter publisher and subscriber interaction."""

import os

from fake_sensors.counter_publisher import CounterPublisher
from fake_sensors.sensor_monitor import SensorMonitor
from fake_sensors.temperature_publisher import TemperaturePublisher

import pytest
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Temperature
from std_msgs.msg import Float32


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

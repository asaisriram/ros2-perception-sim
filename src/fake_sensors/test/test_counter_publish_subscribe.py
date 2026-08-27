"""Test counter publisher and subscriber interaction."""

import os

from fake_sensors.counter_publisher import CounterPublisher
from fake_sensors.counter_subscriber import CounterSubscriber

import pytest
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32


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


class TestnodeSubscriber(Node):
    """Test node created for subscription."""

    def __init__(self, topic_name, msg_type):
        """Initialize test node."""
        super().__init__('testnode_subscriber')
        self.topic_name = topic_name
        self.msg_type = msg_type
        self.msg_data = None
        self.test_subscriber_ = self.create_subscription(
            self.msg_type, self.topic_name, self.testnode_subscriber_callback, 10)

    def testnode_subscriber_callback(self, msg):
        """Return the msg data."""
        self.msg_data = msg.data


def test_counter_publisher(ros_context):
    """Verify that the publisher increments its counter."""
    count = 5
    node_publisher = CounterPublisher()
    for each_spin in range(count):
        rclpy.spin_once(node_publisher, timeout_sec=0.2)
    assert node_publisher.counter == count
    node_publisher.destroy_node()


def test_counter_subscriber(ros_context):
    """Verify that the subscriber receives each published counter."""
    count = 5
    node_publisher = CounterPublisher()
    node_subscriber = CounterSubscriber()
    for _ in range(count):
        rclpy.spin_once(node_publisher, timeout_sec=0.2)
        rclpy.spin_once(node_subscriber, timeout_sec=0.2)
    assert node_subscriber.last_msg == count - 1
    assert node_subscriber.msg_count == count
    node_publisher.destroy_node()
    node_subscriber.destroy_node()


@pytest.mark.parametrize('value, threshold, expected', [
    (499, 500, False),
    (501, 500, True),
])
def test_publish_warning(ros_context, value, threshold, expected):
    """Verify that the subscriber publishes warning."""
    msg = Int32()
    node_subscriber_ = CounterSubscriber()
    testnode_subscriber_ = TestnodeSubscriber('/status/warning', Bool)
    node_subscriber_.threshold = threshold
    msg.data = value
    node_subscriber_.listener_callback(msg)
    rclpy.spin_once(testnode_subscriber_, timeout_sec=0.2)
    assert testnode_subscriber_.msg_data == expected
    node_subscriber_.destroy_node()
    testnode_subscriber_.destroy_node()

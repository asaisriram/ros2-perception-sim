"""Test counter publisher and subscriber interaction."""

import os

from fake_sensors.counter_publisher import CounterPublisher
from fake_sensors.counter_subscriber import CounterSubscriber

import pytest
import rclpy


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


def test_counter_publisher(ros_context):
    """Verify that the publisher increments its counter."""
    count = 5
    node_publisher = CounterPublisher()
    for _ in range(count):
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

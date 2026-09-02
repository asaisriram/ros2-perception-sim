"""Publish messages to a ROS 2 topic."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from fake_sensors import simulation_logic_and_validity


class CounterPublisher(Node):
    """Node publishing counter increments to the topic."""


    def __init__(self):
        """Initialize the counter publisher node."""
        super().__init__('counter_publisher')
        self.publisher_ = self.create_publisher(Float32, '/fake/counter', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)

                                       
    def timer_callback(self):
        """Timer callback function to increment and send counter message."""
        msg = Float32()
        msg.data = simulation_logic_and_validity.get_ground_truth_data(
            self.get_clock().now().nanoseconds)
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing fake counter data: {msg.data}')


def main(args=None):
    """Run the counter publisher node."""
    rclpy.init(args=args)
    node = CounterPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

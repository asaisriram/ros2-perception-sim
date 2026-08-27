"""Subscribe to and record counter messages from a ROS 2 topic."""

from fake_sensors.threshold_logic import is_outside_threshold

import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32


class CounterSubscriber(Node):
    """Record counter messages received from the publisher."""

    def __init__(self):
        """Initialize the counter subscriber node."""
        super().__init__('counter_subscriber')
        self.last_msg = None
        self.msg_count = 0
        self.threshold = 500
        self.subscriber_ = self.create_subscription(
            Int32, '/fake/counter', self.listener_callback, 10)
        self.warning_publisher_ = self.create_publisher(
            Bool, '/status/warning', 10)

    def listener_callback(self, msg):
        """Record a received counter message."""
        self.last_msg = msg.data
        self.msg_count += 1
        self.publish_warning()

    def publish_warning(self):
        """Publish warning when the data is out of limits."""
        status = Bool()
        status.data = is_outside_threshold(self.last_msg, self.threshold)
        self.warning_publisher_.publish(status)
        if status.data:
            self.get_logger().info(
                f'message data: {self.last_msg}, threshold: {self.threshold}')


def main(args=None):
    """Run the counter subscriber node."""
    rclpy.init(args=args)
    node = CounterSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

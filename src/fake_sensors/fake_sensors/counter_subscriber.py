"""Subscribe to and record counter messages from a ROS 2 topic."""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32


class CounterSubscriber(Node):
    """Record counter messages received from the publisher."""

    def __init__(self):
        """Initialize the counter subscriber node."""
        super().__init__('counter_subscriber')
        self.last_msg = None
        self.msg_count = 0
        self.subscriber_ = self.create_subscription(
            Int32, '/fake/counter', self.listener_callback, 10)

    def listener_callback(self, msg):
        """Record a received counter message."""
        self.last_msg = msg.data
        self.msg_count += 1
        self.get_logger().info(f'Subscribed message data: {self.last_msg}')


def main(args=None):
    """Run the counter subscriber node."""
    rclpy.init(args=args)
    node = CounterSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

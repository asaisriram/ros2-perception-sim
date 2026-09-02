"""Publish a simulated temperature sensor reading."""

import random

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Temperature

from fake_sensors import simulation_logic_and_validity


NOISE_C = 0.2   # noise amplitude
temp_offset = simulation_logic_and_validity.TEMP_BASE_C  
temp_factor = simulation_logic_and_validity.TEMP_RATE_C_PER_S

class TemperaturePublisher(Node):
    """Publish a sawtooth temperature signal derived from absolute time."""


    def __init__(self):
        """Initialize the temperature publisher node."""
        super().__init__('temperature_publisher')
        self.temperature_publisher = self.create_publisher(
            Temperature, '/fake/temperature', qos_profile_sensor_data)
        self.timer = self.create_timer(0.25, self.timer_callback)


    def get_sample_temperature(self):
        """Return the modelled temperature at the current instant."""
        time_factored_s = simulation_logic_and_validity.get_ground_truth_data(
            self.get_clock().now().nanoseconds)
        return temp_offset + temp_factor * time_factored_s + random.uniform(
            -NOISE_C, NOISE_C)


    def timer_callback(self):
        """Publish one temperature measurement."""
        msg = Temperature()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'temperature_sensor_link'
        msg.temperature = self.get_sample_temperature()
        msg.variance = 0.0
        self.temperature_publisher.publish(msg)
        self.get_logger().info(f'temperature: {msg.temperature:.2f} C')


def main(args=None):
    """Run the temperature publisher node."""
    rclpy.init(args=args)
    node = TemperaturePublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
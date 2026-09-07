"""Subscribe to sensor topics and publish a derived warning status."""

from fake_sensors import simulation_logic_and_validity
from fake_sensors.simulation_logic_and_validity import ErrorStatus

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Temperature
from std_msgs.msg import Bool, Float32


class SensorMonitor(Node):
    """Cross-check two sensor streams and publish a warning status."""

    def __init__(self):
        """Initialize the sensor monitor node."""
        super().__init__('sensor_monitor')
        self.last_counter = None
        self.last_temperature = None
        self.threshold = 45.0
        self.counter_subscriber = self.create_subscription(
            Float32, '/fake/counter', self.counter_callback, 10)
        self.temperature_subscriber = self.create_subscription(
            Temperature, '/fake/temperature', self.temperature_callback,
            qos_profile_sensor_data)
        self.warning_publisher_ = self.create_publisher(
            Bool, '/status/warning', 10)

    def counter_callback(self, msg):
        """Record a received counter message."""
        self.last_counter = msg.data
        self.publish_warning()

    def temperature_callback(self, msg):
        """Record a received temperature message."""
        self.last_temperature = msg.temperature
        self.publish_warning()

    def list_all_errors(self) -> list:
        """Return the errors currently present, empty if the system is healthy."""
        err_states = []

        inconsistency = simulation_logic_and_validity.is_data_inconsistent(
            self.last_counter, self.last_temperature)
        if inconsistency is not ErrorStatus.NO_ERROR:
            err_states.append(inconsistency)
            return err_states

        threshold_state = simulation_logic_and_validity.is_outside_threshold(
            self.last_counter, self.threshold)
        if threshold_state is not ErrorStatus.NO_ERROR:
            err_states.append(threshold_state)

        plausibility_state = (
            simulation_logic_and_validity.check_sensor_plausibility(
                self.last_counter, self.last_temperature))
        if plausibility_state is not ErrorStatus.NO_ERROR:
            err_states.append(plausibility_state)

        return err_states

    def publish_warning(self):
        """Publish a warning when any error state is active."""
        status = Bool()
        err_states = self.list_all_errors()
        status.data = bool(err_states)
        self.warning_publisher_.publish(status)
        if status.data:
            self.get_logger().info(
                f'Counter: {self.last_counter}, '
                f'threshold: {self.threshold}, '
                f'Temperature: {self.last_temperature}, '
                f'Errors: {err_states}')


def main(args=None):
    """Run the sensor monitor node."""
    rclpy.init(args=args)
    node = SensorMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

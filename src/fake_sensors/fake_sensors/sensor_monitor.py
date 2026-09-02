"""Subscribe to and record sensor messages from a ROS 2 topic."""


from fake_sensors import simulation_logic_and_validity
from fake_sensors.simulation_logic_and_validity import ErrorStatus


import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from std_msgs.msg import Bool, Float32
from sensor_msgs.msg import Temperature


class SensorMonitor(Node):
    """Record sensor messages received from the publisher."""

    def __init__(self):
        """Initialize the counter and temperature subscriber node."""
        super().__init__('sensor_monitor')
        self.last_counter = None
        self.last_temperature = None
        self.threshold = 45.0
        self.counter_subscriber = self.create_subscription(
            Float32, '/fake/counter', self.counter_callback, 10)
        self.temperature_subscriber = self.create_subscription(
            Temperature, '/fake/temperature', self.temperature_callback, qos_profile_sensor_data)
        self.warning_publisher_ = self.create_publisher(
            Bool, '/status/warning', 10)


    def counter_callback(self, msg):
        """Record a received counter message."""
        self.last_counter = msg.data
        #self.get_logger().info(f'Counter: {self.last_counter:.2f}')
        self.publish_warning()


    def temperature_callback(self, msg):
        """Record a received temeprature value."""
        self.last_temperature = msg.temperature
        #self.get_logger().info(f'Temperature: {self.last_temperature:.2f}')
        self.publish_warning()

    def list_all_errors(self) -> list:
        """List all the errors present in system"""
        err_states = []
        err_states.append(simulation_logic_and_validity.is_data_inconsistent(
            self.last_counter, self.last_temperature))
        if ErrorStatus.DATA_INCONSISTENCY_ERROR not in err_states:
            err_states.append(simulation_logic_and_validity.is_outside_threshold(
                self.last_counter, self.threshold))
            err_states.append(
                simulation_logic_and_validity.check_sensor_plausibility(
                self.last_counter, self.last_temperature))
        return err_states
        
    def publish_warning(self):
        """Publish warning when the data is out of limits."""
        status = Bool()
        err_states = self.list_all_errors()
        status.data = all(
            each == ErrorStatus.NO_ERROR for each in err_states)   
        self.warning_publisher_.publish(status)
        if status.data:
            self.get_logger().info(f'Counter: {
                self.last_counter}, threshold: {self.threshold}, Temperature: {
                    self.last_temperature}, Error States: {err_states}')


def main(args=None):
    """Run the counter subscriber node."""
    rclpy.init(args=args)
    node = SensorMonitor()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()

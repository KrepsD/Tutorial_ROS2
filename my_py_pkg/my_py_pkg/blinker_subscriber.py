import rclpy
from rclpy.node import Node
from example_interfaces.msg import Bool

class BlinkerSubscriberNode(Node):
    def __init__(self):
        super().__init__("blinker_subscriber")
        self.subscriber_ = self.create_subscription(Bool, "blinker_status", self.callback_blinker_status, 10)

    def callback_blinker_status(self, msg: Bool):

        if msg.data:
            self.get_logger().info(f"Blinker state updated to ON | LED status: {msg.data}")
        else:
            self.get_logger().info(f"Blinker state updated to OFF | LED status: {msg.data}")

def main(args=None):
    rclpy.init(args=args)
    node = BlinkerSubscriberNode()
    rclpy.spin(node)
    rclpy.shutdown

if __name__ == "main":
    main()
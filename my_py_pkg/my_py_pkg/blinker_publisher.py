import rclpy
from rclpy.node import Node
from example_interfaces.msg import Bool

class BlinkerPublisherNode(Node):
    def __init__(self):
        super().__init__("blinker_publisher")
        self.publisher_ = self.create_publisher(Bool, "blinker_status", 10)
        self.timer_ = self.create_timer(1, self.publish_blinker_status)
        self.last_msg = Bool()
        self.last_msg.data = False
        self.get_logger().info("Sending message to activate blinker")
    
    def publish_blinker_status(self):
        
        msg = Bool()
        msg.data = not self.last_msg.data

        self.publisher_.publish(msg)
        self.last_msg = msg

def main(args=None):
    rclpy.init(args=args)
    node = BlinkerPublisherNode()
    rclpy.spin(node)
    rclpy.shutdown

if __name__ == "main":
    main()
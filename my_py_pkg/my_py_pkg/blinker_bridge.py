import rclpy
from rclpy.node import Node
from example_interfaces.msg import Bool


class BlinkerBridgeNode(Node):

    def __init__(self):
        super().__init__("blinker_bridge")

        self.command_subscriber_ = self.create_subscription(
            Bool,
            "blinker_command",
            self.callback_blinker_command,
            10
        )

        self.status_publisher_ = self.create_publisher(
            Bool,
            "blinker_status",
            10
        )

        self.led_status = False

        self.timer_ = self.create_timer(
                    1.0,
                    self.publish_blinker_status
                )

        self.get_logger().info("Blinker node started")

    def callback_blinker_command(self, msg: Bool):
        desired_state = msg.data

        if desired_state:
            self.get_logger().info("Command received: turn LED ON")
        else:
            self.get_logger().info("Command received: turn LED OFF")

        # enviar comando ao arduino aqui:

        #
        #
        #

    
        # por enquanto, simula a confirmação do arduino
        confirmed_state = desired_state
        
        self.led_status = confirmed_state
        self.publish_blinker_status()

    def publish_blinker_status(self):

        if self.led_status is None:
            # implementar funcao para pegar o estado inicial do arduino
            # (lembrar de mudar sel.led_status para None)
            # exemplo: 
            # self.request_led_status()
            pass
        else:
            status_msg = Bool()
            status_msg.data = self.led_status

            self.status_publisher_.publish(status_msg)

            state_text = "ON" if self.led_status else "OFF"
            self.get_logger().info(
                f"LED status confirmed and published: {state_text}"
            )


def main(args=None):
    rclpy.init(args=args)
    node = BlinkerBridgeNode()
    rclpy.spin(node)
    rclpy.shutdown


if __name__ == "__main__":
    main()
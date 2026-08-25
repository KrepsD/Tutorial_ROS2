import rclpy
from rclpy.node import Node
from example_interfaces.msg import Bool
import javino


class BlinkerBridgeNode(Node):

    def __init__(self):
        super().__init__("blinker_bridge")

        ## javino

        # definição de portas para chamar no terminal
        # ex: ros2 run my_py_pkg blinker_bridge --ros-args -p serial_port:=/dev/ttyUSB0 -p baud_rate:=9600
        self.declare_parameter("serial_port", "/dev/ttyACM0")
        self.declare_parameter("baud_rate", 9600)
        serial_port = self.get_parameter("serial_port").value
        baud_rate = self.get_parameter("baud_rate").value

        # abrir porta com arduino
        self.arduino = javino.start(serial_port, baud_rate)

        if self.arduino is None:
            raise RuntimeError(
                f"Não foi possível abrir a porta {serial_port}"
            )

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

        self.led_status = None

        self.timer_ = self.create_timer(
                    1.0,
                    self.request_led_status
                )
        
        self.serial_read_timer = self.create_timer(
            0.05,
            self.read_arduino_message
        )

        self.get_logger().info("Blinker node started")

    def callback_blinker_command(self, msg: Bool):
        desired_state = msg.data

        if desired_state:
            self.get_logger().info("Command received: turn LED ON")
            command = "ledOn"
        else:
            self.get_logger().info("Command received: turn LED OFF")
            command = "ledOff"

        # enviar comando ao arduino aqui (javino):
        javino.sendMsg(self.arduino, command)
        
        self.get_logger().info(
            f"Comando enviado ao Arduino: {command}"
        )

    def publish_blinker_status(self):

        if self.led_status is None:
            return
        else:
            status_msg = Bool()
            status_msg.data = self.led_status

            self.status_publisher_.publish(status_msg)

            state_text = "ON" if self.led_status else "OFF"
            self.get_logger().info(
                f"LED status confirmed and published: {state_text}"
            )

    # a cada um segundo busca o percept para verificar se o LED está ligado ou desligado
    def request_led_status(self):
        javino.sendMsg(self.arduino, "getPercepts")

    # lê a mensagem do arduino e manda para ser processada no process_percepts e publicada no tópico blinker_status do ros2
    def read_arduino_message(self):
        if self.arduino.in_waiting == 0:
            return

        if not javino.availableMsg(self.arduino):
            return

        message = javino.getMsg()

        if message:
            self.process_percepts(message)

    # 
    def process_percepts(self, message):
        for percept in message.split(";"):
            percept = percept.strip()

            if percept == "ledStatus(on)":
                self.led_status = True
                self.publish_blinker_status()

            elif percept == "ledStatus(off)":
                self.led_status = False
                self.publish_blinker_status()

            elif percept:
                self.get_logger().warning(
                    f"Percepção desconhecida: {percept}"
                )


def main(args=None):
    rclpy.init(args=args)
    node = BlinkerBridgeNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
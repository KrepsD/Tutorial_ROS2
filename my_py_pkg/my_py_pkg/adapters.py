"""Adaptadores que convertem mensagens entre ROS 2 e Javino.

Cada adaptador representa uma categoria de sensor ou atuador descrita no
arquivo YAML. Ele usa a configuração recebida para criar os publishers e
subscribers necessários e para mapear mensagens ROS 2 em ações Javino, ou
percepções Javino em mensagens ROS 2.

Os adaptadores disponíveis inicialmente são:
    - BooleanActuatorAdapter: atuadores com dois estados, como LED e relé;
    - ScalarSensorAdapter: sensores que produzem um valor numérico;
    - DiscreteActuatorAdapter: atuadores com uma lista fixa de comandos,
      como forward, backward e stop.

Exemplos de conversão:
    Bool(data=True) -> ação "ledOn"
    percepção "ledStatus(on)" -> Bool(data=True)
    percepção "distance(32.5)" -> Float32(data=32.5)

BaseAdapter reúne os dados comuns, enquanto ADAPTER_TYPES relaciona o
campo kind do YAML à classe que deve ser criada pela bridge.
"""

from std_msgs.msg import Bool, Float32, String

class BaseAdapter:

    def __init__(self, node, transport, config):
        self.node = node
        self.transport = transport
        self.config = config

        self.name = config["name"]
        self.status_config = config.get("status")

        if self.status_config:
            self.percept_name = self.status_config["percept"]["name"]
        else:
            self.percept_name = None

    def process_percept(self, arguments):
        raise NotImplementedError


class BooleanActuatorAdapter(BaseAdapter):

    EXPECTED_COMMAND_TYPE = "std_msgs/msg/Bool"
    EXPECTED_STATUS_TYPE = "std_msgs/msg/Bool"

    def __init__(self, node, transport, config):
        super().__init__(node, transport, config)

        command_config = config["command"]
        status_config = config["status"]

        self.actions = command_config["actions"]
        self.status_values = status_config["values"]
        self.status_argument = status_config["percept"].get(
            "argument",
            0,
        )

        self.subscription = node.create_subscription(
            Bool,
            command_config["topic"],
            self.command_callback,
            10,
        )

        self.publisher = node.create_publisher(
            Bool,
            status_config["topic"],
            10,
        )

    def command_callback(self, message):
        action_key = "true" if message.data else "false"
        action = self.actions[action_key]

        self.transport.send(action)

        self.node.get_logger().info(
            f"{self.name}: sent Javino action {action}"
        )

    def process_percept(self, arguments):
        if len(arguments) <= self.status_argument:
            self.node.get_logger().warning(
                f"{self.name}: missing percept argument"
            )
            return

        javino_value = arguments[self.status_argument]

        if javino_value not in self.status_values:
            self.node.get_logger().warning(
                f"{self.name}: unknown value {javino_value}"
            )
            return

        ros_value = self.status_values[javino_value]

        message = Bool()
        message.data = ros_value
        self.publisher.publish(message)

class ScalarSensorAdapter(BaseAdapter):

    EXPECTED_STATUS_TYPE = "std_msgs/msg/Float32"

    def __init__(self, node, transport, config):
        super().__init__(node, transport, config)

        status_config = config["status"]
        percept_config = status_config["percept"]
        conversion_config = status_config.get("conversion", {})

        self.argument_index = percept_config.get("argument", 0)

        self.scale = conversion_config.get("scale", 1.0)
        self.offset = conversion_config.get("offset", 0.0)
        self.minimum = conversion_config.get("minimum")
        self.maximum = conversion_config.get("maximum")

        self.publisher = node.create_publisher(
            Float32,
            status_config["topic"],
            10,
        )

    def process_percept(self, arguments):
        if len(arguments) <= self.argument_index:
            self.node.get_logger().warning(
                f"{self.name}: missing percept argument"
            )
            return

        value = float(arguments[self.argument_index])
        value = value * self.scale + self.offset

        if self.minimum is not None:
            value = max(self.minimum, value)

        if self.maximum is not None:
            value = min(self.maximum, value)

        message = Float32()
        message.data = value
        self.publisher.publish(message)


class DiscreteActuatorAdapter(BaseAdapter):

    EXPECTED_COMMAND_TYPE = "std_msgs/msg/String"
    EXPECTED_STATUS_TYPE = "std_msgs/msg/String"

    def __init__(self, node, transport, config):
        super().__init__(node, transport, config)

        command_config = config["command"]
        status_config = config["status"]

        self.actions = command_config["actions"]
        self.status_values = status_config["values"]
        self.status_argument = status_config["percept"].get(
            "argument",
            0,
        )

        self.subscription = node.create_subscription(
            String,
            command_config["topic"],
            self.command_callback,
            10,
        )

        self.publisher = node.create_publisher(
            String,
            status_config["topic"],
            10,
        )

    def command_callback(self, message):
        requested_command = message.data

        if requested_command not in self.actions:
            self.node.get_logger().warning(
                f"{self.name}: invalid command {requested_command}"
            )
            return

        javino_action = self.actions[requested_command]
        self.transport.send(javino_action)

        self.node.get_logger().info(
            f"{self.name}: sent Javino action {javino_action}"
        )

    def process_percept(self, arguments):
        if len(arguments) <= self.status_argument:
            self.node.get_logger().warning(
                f"{self.name}: missing percept argument"
            )
            return

        javino_value = arguments[self.status_argument]

        if javino_value not in self.status_values:
            self.node.get_logger().warning(
                f"{self.name}: unknown value {javino_value}"
            )
            return

        ros_value = self.status_values[javino_value]

        message = String()
        message.data = ros_value
        self.publisher.publish(message)

ADAPTER_TYPES = {
    "boolean_actuator": BooleanActuatorAdapter,
    "scalar_sensor": ScalarSensorAdapter,
    "discrete_actuator": DiscreteActuatorAdapter,
}

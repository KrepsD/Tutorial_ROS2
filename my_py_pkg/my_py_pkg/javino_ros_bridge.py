"""nó principal da bridge entre ROS 2 e Javino.

Este arquivo coordena o funcionamento da bridge. Primeiro, ele carrega o
arquivo YAML com a configuração da porta serial e das interfaces disponíveis.
Depois, cria a comunicação com o Arduino por meio de JavinoIO e instancia
o adaptador correspondente a cada sensor ou atuador descrito no YAML.

Durante a execução, dois timers mantêm a comunicação ativa: um solicita as
percepções do Arduino periodicamente e o outro verifica se uma nova mensagem
chegou pela serial. Cada percepção recebida é separada pelo parser e enviada
ao adaptador responsável por convertê-la e publicá-la no tópico ROS 2 correto.

Fluxo principal:
    YAML -> bridge -> adaptadores -> tópicos ROS 2
    Arduino -> JavinoIO -> parser -> adaptador -> publisher ROS 2
    subscriber ROS 2 -> adaptador -> JavinoIO -> Arduino
"""

import os

import rclpy
from ament_index_python.packages import get_package_share_directory
from rclpy.node import Node

from my_py_pkg.adapters import ADAPTER_TYPES
from my_py_pkg.javino_IO import JavinoIO
from my_py_pkg.perception_parse import perception_parse
import yaml

def load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if config.get("schema_version") != 1:
        raise ValueError("Unsupported YAML schema version")

    if "serial" not in config:
        raise ValueError("Missing serial configuration")

    if "interfaces" not in config:
        raise ValueError("Missing interfaces configuration")

    return config

class JavinoRosBridgeNode(Node):

    def __init__(self):
        super().__init__("javino_ros_bridge")

        default_config_path = os.path.join(
            get_package_share_directory("my_py_pkg"),
            "javino_config",
            "javino_bridge.yaml",
        )

        self.declare_parameter(
            "config_file",
            default_config_path,
        )

        config_path = self.get_parameter("config_file").value
        self.config = load_config(config_path)

        # conexão serial com javino
        serial_config = self.config["serial"]
        self.transport = JavinoIO(serial_config)

        # adaptadores do arquivo de configuração YAML
        self.adapters = []
        self.percept_handlers = {}

        for interface_config in self.config["interfaces"]:
            kind = interface_config["kind"]

            if kind not in ADAPTER_TYPES:
                raise ValueError(
                    f"Unsupported adapter kind: {kind}"
                )

            adapter_class = ADAPTER_TYPES[kind]

            adapter = adapter_class(
                node=self,
                transport=self.transport,
                config=interface_config,
            )

            self.adapters.append(adapter)

            if adapter.percept_name:
                if adapter.percept_name in self.percept_handlers:
                    raise ValueError(
                        f"Duplicated percept: {adapter.percept_name}"
                    )

                self.percept_handlers[adapter.percept_name] = adapter

        # timers para busca na serial
        poll_period = serial_config["percept_poll_period"]
        read_period = serial_config["serial_read_period"]

        self.percept_timer = self.create_timer(
            poll_period,
            self.request_percepts,
        )

        self.serial_read_timer = self.create_timer(
            read_period,
            self.read_serial,
        )

    # solicitar percepções
    def request_percepts(self):
        self.transport.request_percepts()

    # ler as percepcoes e encaminha pro local correto
    def read_serial(self):
        if not self.transport.has_message():
            return

        message = self.transport.read_message()

        if not message:
            return

        for percept_name, arguments in perception_parse(message):
            adapter = self.percept_handlers.get(percept_name)

            if adapter is None:
                self.get_logger().warning(
                    f"Unconfigured percept: {percept_name}"
                )
                continue

            adapter.process_percept(arguments)

def main(args=None):
    rclpy.init(args=args)
    node = JavinoRosBridgeNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()

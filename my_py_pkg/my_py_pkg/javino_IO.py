"""Camada de entrada e saída usada para conversar com o Arduino via Javino.

Este arquivo concentra as operações relacionadas à porta serial. A classe
JavinoIO abre a conexão usando a porta e o baud rate definidos no YAML,
envia ações para o Arduino, solicita percepções e disponibiliza as mensagens
recebidas para o restante da bridge.

Com essa separação, os adaptadores e o nó ROS 2 não precisam conhecer os
detalhes da biblioteca Javino. Eles usam apenas operações simples, como
send(), request_percepts(), has_message() e read_message().

Exemplo de fluxo:
    adaptador -> send("ledOn") -> Javino -> serial -> Arduino
    Arduino -> serial -> Javino -> read_message() -> bridge
"""

import javino

class JavinoIO:

    def __init__(self, serial_config):
        port = serial_config["port"]
        baud_rate = serial_config["baud_rate"]

        self.connection = javino.start(port, baud_rate)

        if self.connection is None:
            raise RuntimeError(
                f"Could not open Javino serial port {port}"
            )

        self.percept_request = serial_config.get(
            "percept_request",
            "getPercepts",
        )

    def send(self, message):
        javino.sendMsg(self.connection, message)

    def request_percepts(self):
        self.send(self.percept_request)

    def has_message(self):
        if self.connection.in_waiting == 0:
            return False

        return javino.availableMsg(self.connection)

    def read_message(self):
        return javino.getMsg()

    def close(self):
        javino.disconnect(self.connection)

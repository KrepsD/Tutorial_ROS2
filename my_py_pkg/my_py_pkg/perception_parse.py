"""Separa as percepções recebidas do Arduino em nome e argumentos.

O Javino pode enviar várias percepções em uma única mensagem, separadas por
ponto e vírgula. A função perception_parse() transforma esse texto em uma
lista de tuplas que a bridge consegue encaminhar aos adaptadores.

Exemplo:
    Entrada: "ledStatus(on);distance(32.5);"
    Saída: [("ledStatus", ["on"]), ("distance", ["32.5"])]

Este parser foi pensado inicialmente para percepções simples no formato
nome(argumento1, argumento2). A interpretação do significado e do tipo de
cada argumento fica sob responsabilidade do adaptador correspondente.
"""

def perception_parse(message):
    parsed_percepts = []

    for raw_percept in message.split(";"):
        raw_percept = raw_percept.strip()

        if not raw_percept:
            continue

        if "(" not in raw_percept or not raw_percept.endswith(")"):
            parsed_percepts.append((raw_percept, []))
            continue

        name, arguments_text = raw_percept[:-1].split("(", 1)

        arguments = [
            argument.strip()
            for argument in arguments_text.split(",")
            if argument.strip()
        ]

        parsed_percepts.append((name.strip(), arguments))

    return parsed_percepts

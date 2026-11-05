"""Диаграмма PlantUML: описание графа и получение картинки от сервера."""

import base64
import zlib

from repository import download

DEFAULT_SERVER = "https://www.plantuml.com/plantuml"
IMAGE_FORMAT = "png"
DEFLATE_WBITS = -zlib.MAX_WBITS
DEFLATE_LEVEL = 9
GROUP_SIZE = 3
TEXT_ENCODING = "utf-8"
BASE64_ALPHABET = (
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
)
PLANTUML_ALPHABET = (
    b"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
)
ALPHABET_TABLE = bytes.maketrans(BASE64_ALPHABET, PLANTUML_ALPHABET)


def plantuml_text(graph):
    """Вернуть описание графа на языке диаграмм PlantUML."""
    ids = {name: f"n{number}" for number, name in enumerate(graph)}
    lines = ["@startuml"]
    for name, node in ids.items():
        lines.append(f'rectangle "{name}" as {node}')
    for name, dependencies in graph.items():
        for dependency in dependencies:
            lines.append(f"{ids[name]} --> {ids[dependency]}")
    lines.append("@enduml")
    return "\n".join(lines)


def encode_text(text):
    """Сжать текст и закодировать так, как требует сервер PlantUML."""
    packer = zlib.compressobj(DEFLATE_LEVEL, zlib.DEFLATED, DEFLATE_WBITS)
    packed = packer.compress(text.encode(TEXT_ENCODING)) + packer.flush()
    packed += bytes(-len(packed) % GROUP_SIZE)
    encoded = base64.b64encode(packed)
    return encoded.translate(ALPHABET_TABLE).decode("ascii")


def image_url(server, text):
    """Вернуть адрес запроса к серверу PlantUML, который отдаёт картинку."""
    return f"{server.rstrip('/')}/{IMAGE_FORMAT}/{encode_text(text)}"


def fetch_image(server, text):
    """Отправить описание диаграммы серверу и вернуть картинку (байты)."""
    return download(image_url(server, text))


def save_image(server, text, path):
    """Получить картинку от сервера и записать её в файл."""
    data = fetch_image(server, text)
    with open(path, "wb") as image_file:
        image_file.write(data)

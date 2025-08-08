from io import BytesIO
from typing import BinaryIO


def to_bytesio(stream: BinaryIO) -> BytesIO:
    stream.seek(0)
    data = stream.read()
    return BytesIO(data)
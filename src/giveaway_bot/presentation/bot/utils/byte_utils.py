import base64
from io import BytesIO
from typing import BinaryIO, Optional


def to_bytesio(stream: BinaryIO) -> BytesIO:
    stream.seek(0)
    data = stream.read()
    return BytesIO(data)


def bytesio_to_base64(bio: BytesIO) -> str:
    bio.seek(0)
    return base64.b64encode(bio.read()).decode('ascii')


def base64_to_bytesio(b64_str: str) -> BytesIO:
    return BytesIO(base64.b64decode(b64_str))


def base64_to_bytes(b64_str: str) -> bytes:
    return base64.b64decode(b64_str)

from dataclasses import dataclass, field, asdict
from typing import Any
import asyncio
import json
import struct
import uuid

HEADER_SIZE = 4  # bytes para el prefijo de longitud


@dataclass
class Request:
    command: str
    params: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self)).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> "Request":
        return cls(**json.loads(data.decode("utf-8")))


@dataclass
class Response:
    request_id: str
    ok: bool
    result: Any = None
    error: str | None = None

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self)).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> "Response":
        return cls(**json.loads(data.decode("utf-8")))


async def send_framed(writer: asyncio.StreamWriter, payload: bytes) -> None:
    header = struct.pack("!I", len(payload))
    writer.write(header + payload)
    await writer.drain()


async def recv_framed(reader: asyncio.StreamReader) -> bytes:
    header = await reader.readexactly(HEADER_SIZE)
    (length,) = struct.unpack("!I", header)
    return await reader.readexactly(length)
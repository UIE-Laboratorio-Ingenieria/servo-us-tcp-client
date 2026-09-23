import asyncio
import logging

from .protocol import (
    Request,
    Response,
    send_framed,
    recv_framed
    )

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

class TCPClient:
    def __init__(
            self,
            host: str,
            port: int = 5050,
            timeout: float = 5.0
            ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

    async def connect(self) -> None:
        self.reader, self.writer = await asyncio.wait_for(
            asyncio.open_connection(self.host, self.port), timeout=self.timeout
        )

    async def close(self) -> None:
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.reader = self.writer = None

    async def __aenter__(self) -> "TCPClient":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def send_command(self, command: str, params: dict | None = None) -> Response:
        if self.writer is None or self.reader is None:
            raise RuntimeError("Cliente no conectado. Llama a connect() primero.")

        req = Request(command=command, params=params or {})
        await send_framed(self.writer, req.to_bytes())

        raw = await asyncio.wait_for(recv_framed(self.reader), timeout=10)
        return Response.from_bytes(raw)


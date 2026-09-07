import asyncio
import logging
import sys
import os
import configparser

from pathlib import Path

sys.path.append(
	os.path.join(
		os.path.dirname(__file__),
		"..",
		"common"
	)
)

from protocol import Request, Response, send_framed, recv_framed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.ini"

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

SERVER_HOST = config.get("server", "host", fallback="127.0.0.1")
SERVER_PORT = config.getint("server", "port", fallback=5050)
class TCPClient:
    def __init__(self, host: str = SERVER_HOST, port: int = SERVER_PORT, timeout: float = 5.0):
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


async def main() -> None:
    async with TCPClient(host=SERVER_HOST, port=SERVER_PORT) as client:
        resp = await client.send_command("gira_servo_raw", {"angle": 90})
        if resp.ok:
            log.info("Giro servo raw: %s", resp.result)
        else:
            log.error("Error del servidor: %s", resp.error)  

        resp = await client.send_command("gira_servo", {"angle": 180})
        if resp.ok:
            log.info("Giro servo: %s", resp.result)
        else:
            log.error("Error del servidor: %s", resp.error)  

        resp = await client.send_command("LecturaUScmRaw")
        if resp.ok:
            log.info("Distancia (cm): %s", resp.result)
        else:
            log.error("Error del servidor: %s", resp.error)  

        resp = await client.send_command("LecturaUScm_Filtrada")
        if resp.ok:
            log.info("Distancia (cm): %s", resp.result)
        else:
            log.error("Error del servidor: %s", resp.error)  

        resp = await client.send_command("realizar_barrido", {"ang_inicio": 0, "ang_fin": 180, "salto_angulo": 20, "retorno_final": True})
        if resp.ok:
            log.info("Distancia (cm): %s", resp.result)
        else:
            log.error("Error del servidor: %s", resp.error)  


if __name__ == "__main__":
    asyncio.run(main())

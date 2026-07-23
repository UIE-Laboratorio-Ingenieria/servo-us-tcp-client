import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "protocol.py"))

import asyncio
import logging
from typing import Callable, Any, Awaitable

from protocol import Request, Response, send_framed, recv_framed

from LibRoombaExtensionConClases import USRotatingSensor




logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

sensor = USRotatingSensor()

# --- Handlers de ejemplo (pueden ser sync o async) -----------------------

async def handle_gira_servo_raw(params: dict) -> Any:
    angle = params.get("angle")
    if angle is None:
        raise ValueError("Falta el parámetro 'angle'")
    await sensor.gira_servo_raw(angle)
    return {"angle_set": angle}

async def handle_gira_servo(params: dict) -> Any:
    angle = params.get("angle")
    if angle is None:
        raise ValueError("Falta el parámetro 'angle'")
    await sensor.gira_servo(angle)
    return {"angle_set": angle}

async def handle_LecturaUScmRaw(params: dict) -> Any:
    resultado = await sensor.LecturaUScmRaw()
    return {"distance_cm": resultado}

async def handle_LecturaUScm_Filtrada(params: dict) -> Any:
    resultado = await sensor.LecturaUScm_Filtrada()
    return {"distance_cm": resultado}

async def handle_realizar_barrido(params: dict) -> Any:
    #ang_inicio=0, ang_fin=180, salto_angulo=20, retorno_final=True
    ang_inicio    = params.get("ang_inicio", 0)
    ang_fin       = params.get("ang_fin", 180)
    salto_angulo  = params.get("salto_angulo", 20)
    retorno_final = params.get("retorno_final", True)
    resultado = await sensor.realizar_barrido(ang_inicio, ang_fin, salto_angulo, retorno_final)

    await sensor.realizar_barrido()
    return {"barrido_result": resultado}

HANDLERS: dict[str, Callable[[dict], Awaitable[Any]]] = {
    "gira_servo_raw": handle_gira_servo_raw,
    "gira_servo": handle_gira_servo,
    "LecturaUScmRaw": handle_LecturaUScmRaw,
    "LecturaUScm_Filtrada": handle_LecturaUScm_Filtrada,
    "realizar_barrido": handle_realizar_barrido
}


# --- Dispatch --------------------------------------------------------------

async def dispatch(req: Request) -> Response:
    handler = HANDLERS.get(req.command)
    if handler is None:
        return Response(request_id=req.request_id, ok=False, error=f"Comando desconocido: {req.command}")
    try:
        result = await handler(req.params)
        return Response(request_id=req.request_id, ok=True, result=result)
    except Exception as e:
        log.exception("Error ejecutando comando %s", req.command)
        return Response(request_id=req.request_id, ok=False, error=str(e))


# --- Manejo de conexión ----------------------------------------------------

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    addr = writer.get_extra_info("peername")
    log.info("Cliente conectado: %s", addr)

    try:
        while True:
            try:
                raw = await recv_framed(reader)
            except asyncio.IncompleteReadError:
                log.info("Cliente desconectado: %s", addr)
                break

            req = Request.from_bytes(raw)
            log.info("Request %s: %s(%s)", req.request_id, req.command, req.params)

            resp = await dispatch(req)
            await send_framed(writer, resp.to_bytes())
    except Exception:
        log.exception("Error inesperado con cliente %s", addr)
    finally:
        writer.close()
        await writer.wait_closed()


async def serve(host: str = "0.0.0.0", port: int = 5050) -> None:
    sensor.setup()  # Configura el sensor antes de aceptar conexiones

    server = await asyncio.start_server(handle_client, host, port)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    log.info("Servidor escuchando en %s", addrs)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(serve())

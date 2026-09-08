# Cliente TCP

Este módulo permite acceder remotamente al servomotor y al sensor de ultrasonidos conectados a una Raspberry Pi mediante una conexión TCP.

El cliente implementa una interfaz sencilla basada en Python asíncrono y oculta todos los detalles del protocolo de comunicación

## Requisitos

* Python 3.10 o superior.
* Conectividad de red con la Raspberry Pi que ejecuta el servidor.
* Acceso al puerto TCP configurado en el servidor (por defecto:: `5050`).

## Estructura

```text
client/
└── tcp_client.py
```

## Conexión al servidor

```python
from tcp_client import TCPClient
import asyncio

async def main():

    async with TCPClient(
        host="IP_DEL_SERVIDOR",
        port=5050
    ) as client:

        print ("Conectado")

asyncio.run(main())
```

## Lectura de distancia

```python
respuesta = await client.send_command(
    "LecturaUScmRaw"
)

print(respuesta.result)
```

Resultado típico:

```python
{
    "distance_cm": 92
}
```

## Lectura filtrada

```python
respuesta = await client.send_command(
    "LecturaUScm_Filtrada"
)

print(respuesta.result)
```

Resultado típico:

```python
{
    "distance_cm": 96
}
```

## Movimiento del servo

### Giro directo

```python
respuesta = await client.send_command(
    "gira_servo_raw",
    {
        "angle": 90
    }
)
```

### Giro controlado

```python
respuesta = await client.send_command(
    "gira_servo",
    {
        "angle": 180
    }
)
```

### Barrido angular

```python
respuesta = await client.send_command(
    "realizar_barrido",
    {
        "ang_inicio": 0,
        "ang_fin": 180,
        "salto_angulo": 20,
        "retorno_final": True
    }
)
```

Ejemplo de respuesta:

```python
{
    "barrido_result": [
        [0, 20, 40, 60, 80, 100, 120, 140, 160, 180],
        [100, 98, 200, 144, 102, 200, 131, 163, 107, 106]
    ]
}
```

## Comandos disponibles

| Comando | Descripción |
|----------|----------|
| `gira_servo_raw` | Posiciona el servomotor en el ángulo indicado. |
| `gira_servo` | Mueve el servomotor aplicando tiempo de estabilización. |
| `LecturaUScmRaw` | Obtiene una lectura directa del sensor ultrasónico. |
| `LecturaUScm_Filtrada` | Obtiene una lectura filtrada del sensor ultrasónico. |
| `realizar_barrido` | Realiza un barrido angular completo. |

## Solución de problemas

### Error de conexión

Si aparece:
```text
ConnectionRefusedError
```

compruebe:

- Que el servidor está ejecutándose.
- Que la dirección IP es la correcta.
- Que el puerto configurado coincide con el del servidor.
- Que existe conectividad de red con la Raspberry Pi.

### Tiempo de espera agotado

Si una petición no recibe respuesta:

- Compruebe que el hardware está correctamente conectado.
- Verifique los registros del servidor.
- Asegúrese de que el sensor de ultrasonidos y el servomotor funcionan correctamente.
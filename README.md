# servo-us-tcp-client

## 1. Objetivo

Proporciona una forma simple y directa para el control de un sensor ultrasónico montado sobre un servomotor conectado a una Raspberry Pi, permitiendo realizar mediciones de distancia y barridos angulares desde aplicaciones Python.

La librería está orientada principalmente a docencia, prácticas de laboratorio y prototipado rápido de aplicaciones de robótica móvil y sensorización, ofreciendo una API sencilla basada en Python asíncrono.

Además de la ejecución local sobre la Raspberry Pi, el proyecto incluye una arquitectura cliente-servidor basada en TCP que permite acceder remotamente al hardware desde cualquier ordenador de la misma red, facilitando el desarrollo distribuido y el acceso compartido a los dispositivos del laboratorio.

Los principales casos de uso son:

* Medición de distancias mediante sensores ultrasónicos.
* Realización de barridos angulares para detección de obstáculos.
* Generación de mapas unidimensionales del entorno.
* Prácticas docentes de programación asíncrona con Python.
* Acceso remoto a hardware conectado a Raspberry Pi mediante sockets TCP.
* Proyectos de robótica móvil y navegación basada en sensores de distancia.

## 2. Características

* Control de un servo de 180º mediante Raspberry Pi y GPIO Zero.
* Lectura de distancias utilizando sensores ultrasónicos compatibles con HC-SR04 o similares.
* Medición directa de distancia en centímetros.
* Filtrado automático de lecturas para reducir el efecto de valores espurios.
* Realización de barridos angulares configurables.
* API basada en programación asíncrona mediante asyncio.
* Gestión automática de recursos hardware mediante context managers.
* Registro opcional de actividad mediante ficheros de log.
* Arquitectura cliente-servidor basada en TCP.
* Acceso remoto al hardware desde cualquier equipo de la misma red.
* Protocolo de comunicación sencillo basado en mensajes JSON.
* Orientado a la docencia, prácticas de laboratorio y prototipado rápido de aplicaciones de robótica.
  
## 3. Instalación

#### Requisitos cliente
* Windows 10/11, macOS o Linux.
* Python 3.10 o superior.
* Conectividad de red con la Raspberry Pi.

#### Requisitos servidor

* Raspberry Pi 4 o superior.
* Sensor ultrasónico HC-SR04 o compatible.
* Servo de 180°.
* Python 3.10 o superior.
* Servicio pigpiod.

#### Clonar el repositorio

```bash
git clone https://github.com/UIE-Laboratorio-Ingenieria/servo-us-tcp-client.git

cd servo-us-tcp-client
```

#### Crear y activar un entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Verificar que el entorno virtual está activo

```bash
which python
which pip
```

La salida debe apuntar a la carpeta `.venv`

#### Instalar las dependencias

```bash
pip install --upgrade pip
pip install -r ClienteServidor/requirements.txt
```

#### Verificar la instalación de las dependencias

```bash
python -c "import gpiozero; print('gpiozero OK')"
python -c "import pigpio; print('pigpio OK')"
```

La salida esperada es:
```bash
gpiozero OK
pigpio OK
```

## 4. Quick Start

#### Uso local

Crear una instancia de la clase `USRotatingSensor`, inicializar el hardware y realizar un barrido angular:

```python
from LibRoombaExtensionConClases import USRotatingSensor
import asyncio

async def main():

    with USRotatingSensor() as sensor:
        sensor.setup()

        angulos, lecturas = await sensor.realizar_barrido(
            ang_inicio=0,
            ang_fin=180,
            salto_angulo=20,
        )

        print(angulos)
        print(lecturas)

asyncio.run(main())
```

#### Uso mediante TCP

```bash
python RoombaExtensionServidorTCP.py
```

Desde cualquier equipo de la misma red utilizando el cliente:

```python
from RoombaExtensionClienteTCP import TCPClient
import asyncio

async def main():
    async with TCPClient(
        host="192.168.1.100",
        port=5050
    ) as client:

        respuesta = await client.send_command(
            "realizar_barrido",
            {
                "ang_inicio": 0,
                "ang_fin": 180,
                "salto_angulo": 20,
            }
        )
        print(respuesta.result)
asyncio.run(main())
```
#### Resultado esperado

La librería devuelve dos listas:

* Lista de ángulos.
* Lista de distancias medidas en centímetros.

Por ejemplo:

```python
(
[0, 20, 40, 60, 80, 100, 120, 140, 160, 180],
[85, 82, 78, 74, 70, 71, 76, 81, 84, 87]
)
```

## 5. Arquitectura Cliente-Servidor

La librería puede utilizarse tanto de forma local sobre una Raspberry Pi como mediante una arquitectura cliente-servidor basada en TCP.

```text
            +--------------------+
            | Aplicación Cliente |
            +---------+----------+
                      |
                      | TCP / JSON
                      |
            +---------v----------+
            |    Servidor TCP    |
            +---------+----------+
                      |
                      |
            +---------v----------+
            |  USRotatingSensor  |
            +---------+----------+
                      |
                +-----+-----+
                |           |
                v           v
              Servo      HC-SR04
```

#### Cliente

El cliente implementa una interfaz sencilla para enviar comandos al servidor mediante TCP. Cada petición se codifica en formato `JSON` y se transmite utlizando un protocolo de mensajes con longitud prefijada.

#### Protocolo

El archivo `protocol.py` define:

* Estructura de peticiones (`Request`).
* Estructura de respuestas (`Response`).
* Serialización JSON.
* Envío y recepción de mensajes TCP enmarcados.

#### Servidor

El servidor recibe las peticiones TCP, ejecuta la operación correspondiente sobre una instancia de `USRotatingSensor` y devuelve el resultado al cliente.

#### Hardware



## 6. API
## 7. Ejemplos
## 8. Limitaciones
## 9. Licencia
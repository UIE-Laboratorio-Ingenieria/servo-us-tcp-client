# servo-us-tcp-client

## 1. Objetivo

Proporcionar una forma sencilla y directa de controlar remotamente un sensor ultrasónico montado sobre un servomotor y conectado a una Raspberry Pi, permitiendo realizar mediciones de distancia y barridos angulares desde aplicaciones Python.

El proyecto está orientado principalmente a la docencia, las prácticas de laboratorio y el prototipado rápido de aplicaciones de robótica móvil y sensorización. Para facilitar su utilización por parte de los estudiantes, ofrece una API asíncrona que permite acceder al hardware sin necesidad de gestionar directamente los GPIO de la Raspberry Pi ni los detalles internos de la comunicación de red.

La solución utiliza una arquitectura cliente-servidor basada en TCP:

- El servidor se ejecuta en la Raspberry Pi y gestiona el servomotor y el sensor ultrasónico.
- La librería cliente puede instalarse desde PyPI y utilizarse desde equipos con Windows, Linux o macOS.
- La comunicación se realiza mediante mensajes JSON transmitidos a través de una conexión TCP.
- El cliente y el servidor pueden utilizarse dentro de una red local, mediante una conexión Ethernet directa o a través de la infraestructura de red disponible.

La librería cliente puede instalarse mediante:

```bash
pip install servo-us-tcp-client
```

## 2. Características

- Control remoto de un servomotor de 180° conectado a una Raspberry Pi.
- Lectura de distancias mediante un sensor ultrasónico HC-SR04 o compatible.
- Obtención de medidas directas en centímetros.
- Filtrado estadístico de lecturas para reducir valores espurios.
- Realización de barridos angulares configurables.
- Arquitectura cliente-servidor basada en TCP.
- Protocolo de comunicación basado en mensajes JSON con longitud prefijada.
- API asíncrona desarrollada con `asyncio`.
- Librería cliente instalable desde PyPI mediante `pip`.
- Uso de la librería mediante `from servoclient import TCPClient`.
- Compatibilidad del cliente con Windows, Linux y macOS.
- Configuración del host, puerto y tiempo de espera desde la aplicación cliente.
- Gestión automática de la conexión mediante context managers asíncronos.
- Gestión segura de los recursos hardware mediante context managers.
- Lectura remota del sensor y control del servomotor desde cualquier equipo con conectividad TCP hacia la Raspberry Pi.
- Integración con otras librerías del laboratorio, como `rplidar-tcp-client`.
- Registro de la actividad del servidor mediante ficheros de log y el diario de `systemd`.
- Arranque automático del servidor en la Raspberry Pi mediante `systemd`.
- Orientado a la docencia, las prácticas de laboratorio y el prototipado de aplicaciones de robótica móvil.

## 3. Estructura del repositorio

```text
servo-us-tcp-client/
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── LICENSE
├── pyproject.toml
├── config.example.ini
├── .gitignore
│
├── src/
│   └── servoclient/
│       ├── __init__.py
│       ├── protocol.py
│       └── tcp_client.py
│
├── client/
│   ├── README.md
│   └── tcp_client.py
│
├── server/
│   ├── README.md
│   ├── requirements.txt
│   ├── tcp_server.py
│   └── us_rotating_sensor.py
│
├── common/
│   └── protocol.py
│
├── examples/
│   └── basic_scan.py
│
└── docs/
    ├── images/
    ├── laboratory-setup.md
    └── troubleshooting.md
```

### Componentes principales
- `src/servoclient/`: código fuente de la librería cliente distribuida mediante PyPI.
- `src/servoclient/tcp_client.py`: implementación de la clase pública `TCPClient`.
- `src/servoclient/protocol.py`: estructuras y funciones utilizadas por el protocolo TCP.
- `client/`: cliente ejecutable incluido en el repositorio y su documentación específica.
- `server/`: servidor TCP, lógica de acceso al hardware y dependencias para Raspberry Pi.
- `common/`: implementación compartida del protocolo utilizada por los scripts del repositorio.
- `examples/`: ejemplos de utilización local y remota.
- `docs/`: documentación de instalación, mantenimiento y resolución de problemas.
- `pyproject.toml`: configuración de construcción y distribución del paquete Python.
- `config.example.ini`: ejemplo de configuración para los scripts cliente incluidos en el repositorio.

## 4. Instalación

El procedimiento depende del uso que se vaya a hacer del proyecto:
 
- Los estudiantes y desarrolladores que sólo necesiten acceder remotamente al hardware pueden instalar la librería cliente desde PyPI.
- Los administradores que necesiten desplegar el servidor en una Raspberry Pi deben clonar el repositorio e instalar las dependencias específicas del hardware.

### 4.1. Instalación de la librería cliente
 
#### Requisitos
 
- Windows 10/11, macOS o Linux.
- Python 3.10 o superior.
- Conectividad TCP con la Raspberry Pi que ejecuta el servidor.
 
#### Crear y activar un entorno virtual
 
En Linux o macOS:
 
```bash
python3 -m venv .venv
source .venv/bin/activate
```

En Windows PowerShell

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Actualizar `pip`

```bash
python -m pip install --upgrade pip
```

#### Instalar desde PyPI

```bash
python -m pip install servo-us-tcp-client
```

#### Verificar la instalación

```bash
python -c "from servoclient import TCPClient; print('servo-us-tcp-client OK')"
```

La salida esperada es: ```servo-us-tcp-client OK```

La clase cliente puede importarse mediante:

```bash
from servoclient import TCPClient
```

> NOTA: La librería cliente no necesita `gpiozero`, `lgpio` ni acceso a los GPIO. Estas dependencias se utilizan exclusivamente en la Raspberry Pi que ejecuta el servidor.

### 4.2. Instalación desde el repositorio

Esta opción está orientada al desarrollo, la ejecución de los ejemplos y el despliegue del servidor.

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
#### Actualizar `pip`

```bash
python -m pip install --upgrade pip
```
#### Instalar la librería cliente en modo editable

```bash
python -m pip install -e .
```

Esta instalación permite utilizar:

```bash
from servoclient import TCPClient
```

Los cambios realizados en `src/servoclient/` estarán disponibles inmediatamente sin necesidad de reinstalar el paquete.

#### Verificar la instalación editable

```bash
python -c "from servoclient import TCPClient; print(TCPClient)"
```

### 4.3. Instalación del servidor en Raspberry Pi

#### Requisitos de hardware

* Raspberry Pi 4 o superior
* Sensor ultrasónico HC-SR04 o compatible
* Servomotor de 180º
* Divisor de tensión o adaptador de nivel lógico para la señal `ECHO`
* Conectividad de red

#### Requisitos de software

* Ubuntu 24.04 LTS o sistema compatible.
* Python 3.10 o superior
* Git
* Soporte GPIO mediante `lgpio`

#### Instalar las dependencias del servidor

Desde la raíz del repositorio y con el entorno virtual activado:

```bash
python -m pip install -r server/requirements.txt
```

#### Verificar las dependencias

```bash
python -c "import gpiozero; print('gpiozero OK')"
python -c "import lgpio; print('lgpio OK')"
```

La salida esperada es: 

```bash 
gpiozero OK
lgpio OK
```

#### Arrancar el servidor manualmente

```bash
python server/tcp_server.py
```
La salida esperada es:

```bash
Servidor escuchando en ('0.0.0.0', 5050)
```

> NOTA: Las instrucciones completas de conexión del hardware, despliegue mediante `systemd` y verificación están disponibles en `server/README.md` y `docs/laboratory-setup.md`


### 4.4. Configuración para el cliente ejecutable del repositorio

Esta configuración sólo es necesaria para ejecutar directamente:

```bash
python client/tcp_client.py
```

No es obligatoria cuando se utiliza la librería instalada desde PyPI, ya que `TCPClient` recibe el host y el puerto como argumentos.

Crear el fichero local:

```bash
cp config.example.ini config.ini
```

En Windows `PowerShell`

```bash
Copy-Item config.example.ini config.ini
```

Editar `config.ini`

```bash
[server]
host = 192.168.50.1
port = 5050
```

Donde:
* `host` es la dirección IP de la Raspberry Pi que ejecuta el servidor
* `port` es el puerto TCP del servicio, `5050` de forma predeterminada.

Configuración correcta:

```bash
host = 192.168.50.1
```

Configuración incorrecta:

```bash
host = "192.168.50.1"
```

El archivo `config.ini` es local, está excluido mediante `.gitignore` y no debe incorporarse al repositorio.

## 5. Uso local en la Raspberry Pi.

El acceso local permite controlar directamente el servomotor y el sensor ultrasónico sin utilizar la comunicación TCP.

Este modo está orientado principalmente a:

* Comprobar el cableado y el funcionamiento del hardware.
* Realizar tareas de mantenimiento.
* Diagnosticar problemas del sensor o del servomotor.
* Desarrollar y probar nuevas funcionalidades del servidor.

> NOTA: El uso local requiere ejecutar el código en la Raspberry Pi con el repositorio clonado y las dependencias del servidor instaladas. La clase `USRotatingSensor` no forma parte de la librería cliente distribuida mediante PyPI.

### 5.1. Requisitos previos

Desde la raíz del repositorio:

```bash
source .venv/bin/activate
python -m pip install -r server/requirements.txt
```

El hardware debe estar conectado de acuerdo con la configuración predeterminada:

```text
Servo PWM   -> GPIO18
HC-SR04 TRIG -> GPIO17
HC-SR04 ECHO -> GPIO27
```

La señal `ECHO` del HC-SR04 debe conectarse mediante un divisor de tensión o un adaptador de nivel lógico.

### 5.2. Barrido angular local

Ejecutar el ejemplo incluido en el repositorio:

```bash
python examples/basic_scan.py
```

El ejemplo debe inicializar el hardware, realizar un barrido angular y liberar los recursos al finalizar.

Una implementación equivalente es:

```python
import asyncio

from us_rotating_sensor import USRotatingSensor


async def main():
    with USRotatingSensor() as sensor:
        sensor.setup()

        angulos, distancias = await sensor.realizar_barrido(
            ang_inicio=0,
            ang_fin=180,
            salto_angulo=20,
            retorno_final=True,
        )

        for angulo, distancia in zip(angulos, distancias):
            print(f"{angulo:3d}° -> {distancia} cm")


asyncio.run(main())
```

> NOTA: Este ejemplo presupone que `us_rotating_sensor.py` puede importarse desde el directorio de ejecución. Se recomienda utilizar `examples/basic_scan.py`, que debe contener la configuración de importación correspondiente a la estructura actual del repositorio.

### 5.3. Lectura directa

Para obtener una única medida sin aplicar filtrado:

```python
distancia = await sensor.LecturaUScmRaw()
print(f"Distancia: {distancia} cm")
```

### 5.4. Lectura filtrada

Para reducir el efecto de las lecturas espurias:

```python
distancia = await sensor.LecturaUScm_Filtrada(
    num_medidas=5,
    umbral_tolerancia=2.0,
)

print(f"Distancia filtrada: {distancia} cm")
```

### 5.5. Movimiento del servomotor

Para mover el servomotor y esperar a que complete el desplazamiento

```python
await sensor.gira_servo(90)
```

El proyecto libera la señal `PWM` después del movimiento para evitar microtemblores en reposo con determinados modelos de servomotor.

### 5.6. Resultado esperado

Un barrido devuelve dos listas:

1. Los ángulos recorridos.
2. Las distancias medidas en centímetros.

Por ejemplo:

```text
(
    [0, 20, 40, 60, 80, 100, 120, 140, 160, 180],
    [85, 82, 78, 74, 70, 71, 76, 81, 84, 87],
)
```

### 5.7. Liberación de recursos

La forma recomendada de utilizar `USRotatingSensor` es mediante un bloque `with`:

```python
with USRotatingSensor() as sensor:
    sensor.setup()
    # Operaciones con el hardware
```

Al salir del bloque se ejecuta automáticamente `cleanup()`, que libera el sensor, el servomotor y los recursos GPIO.


## 6. Arquitectura Cliente-Servidor

El proyecto separa el acceso al hardware de las aplicaciones que lo utilizan. El servidor se ejecuta en la Raspberry Pi, mientras que los clientes pueden ejecutarse en Windows, Linux o macOS.

```text
        +------------------------------+
        | Aplicación Python            |
        |                              |
        | from servoclient import      |
        | TCPClient                    |
        +---------------+--------------+
                        |
                        | TCP / JSON
                        | Puerto 5050
                        |
        +---------------v--------------+
        | Servidor TCP                 |
        | server/tcp_server.py         |
        +---------------+--------------+
                        |
        +---------------v--------------+
        | USRotatingSensor             |
        | server/us_rotating_sensor.py |
        +---------------+--------------+
                        |
                +-----+-----+
                |           |
                v           v
            Servomotor     HC-SR04
```

### 6.1. Cliente

La librería cliente se distribuye mediante PyPI:

```shell
python -m pip install servo-us-tcp-client
```

La clase pública se importa mediante:

```python
from servoclient import TCPClient
```

`TCPClient` establece la conexión, envía comandos y recibe las respuestas del servidor. La conexión puede gestionarse automáticamente mediante un context manager asíncrono:

```python
async with TCPClient(
    host="192.168.50.1",
    port=5050,
) as client:
    respuesta = await client.send_command("LecturaUScmRaw")
```

### 6.2. Protocolo

Cada petición contiene:

* Un identificador.
* El nombre del comando.
* Un diccionario de parámetros.

Cada respuesta contiene:

* El identificador de la petición.
* El estado de la operación.
* El resultado o la descripción del error.

### 6.3. Servidor

El servidor escucha de forma predeterminada en :

```text
0.0.0.0:5050
```

Cuando recibe una petición:

  1. Deserializa el mensaje.
  2. Identifica el comando solicitado.
  3. Ejecuta la operación sobre `USRotatingSensor`.
  4. Serializa el resultado.
  5. Devuelve la respuesta al cliente.

En la Raspberry Pi, el servidor puede ejecutarse automáticamente mediante:

```text
servo-us-server.service
```

### 6.4. Hardware

El acceso al hardware se realiza exclusivamente en la Raspberry Pi.

La clase `USRotatingSensor` encapsula:

* Control del servomotor.
* Lectura del sensor de ultrasonidos.
* Filtrado de medidas para reducir lecturas espurias.
* Realización de barridos angulares configurables.
* Liberación de señal PWM para evitar microtemblores.
* Gestión automática de recursos hardware.

Esta separación permite que las aplicaciones cliente utilicen el hardware sin depender de `gpiozero`, `lgpio` ni de una Raspberry Pi local.

## 7. API

El proyecto proporciona dos interfaces diferenciadas:

- `TCPClient`: API pública incluida en el paquete `servo-us-tcp-client` y destinada a aplicaciones remotas.
- `USRotatingSensor`: API local utilizada por el servidor para acceder al hardware conectado a la Raspberry Pi.

### 7.1. Clase `TCPClient`

La clase `TCPClient` permite conectarse al servidor TCP, enviar comandos y recibir sus resultados.

Se importa mediante:

```python
from servoclient import TCPClient
```

#### Constructor

```python
TCPClient(
host,
port=5050,
timeout=5.0,
)
```
 
Parámetros:
 
- `host`: dirección IP o nombre del servidor.
- `port`: puerto TCP del servidor. El valor predeterminado es `5050`.
- `timeout`: tiempo máximo, en segundos, para establecer la conexión.
 
Ejemplo:
 
```python
client = TCPClient(
host="192.168.50.1",
port=5050,
timeout=5.0,
)
```

#### connect()
 
Establece la conexión TCP con el servidor.
 
```python
await client.connect()
```
 
Si no se puede completar la conexión dentro del tiempo configurado, se genera una excepción de conexión o tiempo de espera.
 
#### close()
 
Cierra la conexión TCP y libera los recursos asociados.
 
```python
await client.close()
```
#### send_command()
 
Envía un comando al servidor y espera su respuesta.
 
```python
respuesta = await client.send_command(
command,
params=None,
)
```
 
Parámetros:
 
- `command`: nombre del comando remoto.
- `params`: diccionario con los parámetros del comando. Es opcional.
 
Devuelve un objeto `Response`.
 
Ejemplo:
 
```python
respuesta = await client.send_command(
"gira_servo",
{
"angle": 90,
},
)
```

#### Uso mediante context manager
 
La forma recomendada de gestionar la conexión es utilizar un context manager asíncrono:
 
```python
import asyncio
 
from servoclient import TCPClient
 
 
async def main():
async with TCPClient("192.168.50.1") as client:
respuesta = await client.send_command("LecturaUScmRaw")
 
if respuesta.ok:
print(respuesta.result)
else:
print(respuesta.error)
 
 
asyncio.run(main())
```
 
Al salir del bloque se cierra automáticamente la conexión.
 
 
### 7.2. Objeto Response
 
Cada llamada a `send_command()` devuelve un objeto `Response`.
 
Los atributos utilizados habitualmente son:
 
- `ok`: indica si la operación se completó correctamente.
- `result`: contiene el resultado cuando `ok` es `True`.
- `error`: contiene la descripción del error cuando `ok` es `False`.
 
Ejemplo:
 
```python
respuesta = await client.send_command("LecturaUScmRaw")
 
if respuesta.ok:
distancia = respuesta.result["distance_cm"]
print(f"Distancia: {distancia} cm")
else:
print(f"Error del servidor: {respuesta.error}")
```

### 7.3. Comandos TCP disponibles

#### gira_servo_raw
 
Posiciona directamente el servomotor en el ángulo indicado.
 
Parámetros:
 
- `angle`: ángulo solicitado, entre 0° y 180°.
 
```python
respuesta = await client.send_command(
"gira_servo_raw",
{
"angle": 90,
},
)
```
 
Resultado típico:
 
```python
{
"angle_set": 90
}
```

#### gira_servo
 
Mueve el servomotor al ángulo indicado y espera el tiempo calculado para completar el desplazamiento.
 
Parámetros:
 
- `angle`: ángulo solicitado, entre 0° y 180°.
 
```python
respuesta = await client.send_command(
"gira_servo",
{
"angle": 180,
},
)
```
 
Resultado típico:
 
```python
{
"angle_set": 180
}
```
#### LecturaUScmRaw
 
Obtiene una lectura directa del sensor ultrasónico.
 
No requiere parámetros:
 
```python
respuesta = await client.send_command(
"LecturaUScmRaw"
)
```
 
Resultado típico:
 
```python
{
"distance_cm": 85
}
```

#### LecturaUScm_Filtrada
 
Realiza varias mediciones y devuelve una lectura filtrada.
 
No requiere parámetros en la API TCP actual:
 
```python
respuesta = await client.send_command(
"LecturaUScm_Filtrada"
)
```
 
Resultado típico:
 
```python
{
"distance_cm": 84
}
```

#### realizar_barrido
 
Realiza un barrido angular y devuelve los ángulos recorridos y las distancias medidas.
 
Parámetros:
 
- `ang_inicio`: ángulo inicial.
- `ang_fin`: ángulo final.
- `salto_angulo`: incremento angular entre mediciones.
- `retorno_final`: indica si el servomotor debe regresar a la posición inicial al terminar.
 
```python
respuesta = await client.send_command(
"realizar_barrido",
{
"ang_inicio": 0,
"ang_fin": 180,
"salto_angulo": 20,
"retorno_final": True,
},
)
```
 
Resultado típico:
 
```python
{
"barrido_result": [
[0, 20, 40, 60, 80, 100, 120, 140, 160, 180],
[85, 82, 78, 74, 70, 71, 76, 81, 84, 87]
]
}
```

### 7.4. Clase USRotatingSensor
 
La clase `USRotatingSensor` proporciona acceso local al servomotor y al sensor ultrasónico conectados a la Raspberry Pi.
 
Esta clase forma parte del servidor y no está incluida en el paquete cliente instalado desde PyPI.
 
#### setup()
 
Inicializa el sensor ultrasónico y el servomotor.
 
```python
sensor.setup()
```

#### cleanup()
 
Libera los recursos GPIO utilizados por el sensor y el servomotor.
 
```python
sensor.cleanup()
```
 
Cuando se utiliza un bloque `with`, la limpieza se realiza automáticamente:
 
```python
with USRotatingSensor() as sensor:
sensor.setup()
```

#### LecturaUScmRaw()
 
Obtiene una lectura directa del sensor ultrasónico en centímetros.
 
```python
distancia = await sensor.LecturaUScmRaw()
```

#### LecturaUScm_Filtrada()
 
Obtiene varias medidas, elimina valores espurios y devuelve una distancia filtrada.
 
```python
distancia = await sensor.LecturaUScm_Filtrada(
num_medidas=5,
umbral_tolerancia=2.0,
)
```

Parámetros:
 
- `num_medidas`: número de muestras utilizadas.
- `umbral_tolerancia`: separación máxima respecto a la mediana para aceptar una medida.
 
#### gira_servo_raw()
 
Posiciona directamente el servomotor en el ángulo indicado.
 
```python
await sensor.gira_servo_raw(90)
```

#### gira_servo()
 
Mueve el servomotor al ángulo indicado, espera a que finalice el desplazamiento y libera posteriormente la señal PWM.
 
```python
await sensor.gira_servo(90)
```
 
La liberación de la señal PWM evita microtemblores en reposo con determinados modelos de servomotor.
 
#### realizar_barrido()
 
Realiza un barrido angular y devuelve dos listas:
 
1. Ángulos recorridos.
2. Distancias medidas en centímetros.
 
```python
angulos, distancias = await sensor.realizar_barrido(
ang_inicio=0,
ang_fin=180,
salto_angulo=20,
retorno_final=True,
)
```
 
Ejemplo de resultado:
 
```python
(
[0, 20, 40, 60, 80, 100, 120, 140, 160, 180],
[85, 82, 78, 74, 70, 71, 76, 81, 84, 87],
)
```

## 8. Ejemplos

Los siguientes ejemplos muestran cómo utilizar la librería cliente instalada desde PyPI y cómo acceder localmente al hardware desde la Raspberry Pi.

### 8.1. Lectura remota de distancia

Obtener una lectura directa del sensor ultrasónico desde una aplicación cliente:

```python
import asyncio

from servoclient import TCPClient


async def main():
    async with TCPClient(
        host="192.168.50.1",
        port=5050,
    ) as client:
        respuesta = await client.send_command(
            "LecturaUScmRaw"
        )

        if respuesta.ok:
            distancia = respuesta.result["distance_cm"]
            print(f"Distancia: {distancia} cm")
        else:
            print(f"Error del servidor: {respuesta.error}")


asyncio.run(main())
```

Salida típica:

```text
Distancia: 85 cm
```

---

### 8.2. Lectura remota filtrada

Obtener una lectura filtrada para reducir el efecto de medidas espurias:

```python
import asyncio

from servoclient import TCPClient


async def main():
    async with TCPClient("192.168.50.1") as client:
        respuesta = await client.send_command(
            "LecturaUScm_Filtrada"
        )

        if respuesta.ok:
            distancia = respuesta.result["distance_cm"]
            print(f"Distancia filtrada: {distancia} cm")
        else:
            print(f"Error del servidor: {respuesta.error}")


asyncio.run(main())
```

---

### 8.3. Movimiento remoto del servomotor

Mover el servomotor hasta un ángulo determinado:

```python
import asyncio

from servoclient import TCPClient


async def main():
    async with TCPClient("192.168.50.1") as client:
        respuesta = await client.send_command(
            "gira_servo",
            {
                "angle": 90,
            },
        )

        if respuesta.ok:
            print(
                f"Ángulo establecido: "
                f"{respuesta.result['angle_set']}°"
            )
        else:
            print(f"Error del servidor: {respuesta.error}")


asyncio.run(main())
```

---

### 8.4. Barrido angular remoto

Realizar un barrido angular completo desde una aplicación cliente:

```python
import asyncio

from servoclient import TCPClient


async def main():
    async with TCPClient("192.168.50.1") as client:
        respuesta = await client.send_command(
            "realizar_barrido",
            {
                "ang_inicio": 0,
                "ang_fin": 180,
                "salto_angulo": 20,
                "retorno_final": True,
            },
        )

        if not respuesta.ok:
            print(f"Error del servidor: {respuesta.error}")
            return

        angulos, distancias = respuesta.result["barrido_result"]

        for angulo, distancia in zip(angulos, distancias):
            print(f"{angulo:3d}° -> {distancia} cm")


asyncio.run(main())
```

Salida típica:

```text
  0° -> 85 cm
 20° -> 82 cm
 40° -> 78 cm
 60° -> 74 cm
 80° -> 70 cm
100° -> 71 cm
120° -> 76 cm
140° -> 81 cm
160° -> 84 cm
180° -> 87 cm
```

---

### 8.5. Uso conjunto con rplidar-tcp-client

Las dos librerías pueden instalarse y utilizarse dentro del mismo entorno virtual:

```bash
python -m pip install \
    rplidar-tcp-client \
    servo-us-tcp-client
```

Ejemplo de utilización conjunta:

```python
import asyncio

from lidarclient import LidarClient
from servoclient import TCPClient


RASPBERRY_HOST = "192.168.50.1"


def obtener_barrido_lidar():
    with LidarClient(
        RASPBERRY_HOST,
        port=5000,
        scan_mode="express",
    ) as lidar:
        scan = lidar.get_scan()

    print(f"Puntos LIDAR recibidos: {len(scan)}")
    return scan


async def obtener_distancia_ultrasonica():
    async with TCPClient(
        RASPBERRY_HOST,
        port=5050,
    ) as client:
        respuesta = await client.send_command(
            "LecturaUScmRaw"
        )

        if not respuesta.ok:
            raise RuntimeError(respuesta.error)

        distancia = respuesta.result["distance_cm"]
        print(f"Distancia ultrasónica: {distancia} cm")
        return distancia


async def main():
    scan = obtener_barrido_lidar()
    distancia = await obtener_distancia_ultrasonica()

    print(f"Medidas LIDAR: {len(scan)}")
    print(f"Distancia ultrasónica: {distancia} cm")


asyncio.run(main())
```

Este ejemplo utiliza simultáneamente:

```text
Puerto 5000 -> RPLIDAR
Puerto 5050 -> Servo y sensor ultrasónico
```

---

### 8.6. Lectura local en la Raspberry Pi

El acceso local está orientado a pruebas de hardware y mantenimiento del servidor.

```python
import asyncio

from us_rotating_sensor import USRotatingSensor


async def main():
    with USRotatingSensor() as sensor:
        sensor.setup()

        distancia = await sensor.LecturaUScmRaw()

        print(f"Distancia: {distancia} cm")


asyncio.run(main())
```

> Este código debe ejecutarse en la Raspberry Pi con el repositorio clonado y las dependencias del servidor instaladas. Para evitar problemas de importación, se recomienda utilizar los ejemplos incluidos en la carpeta `examples/`.

---

### 8.7. Gestión automática de recursos

La librería cliente debe utilizarse preferentemente mediante un context manager asíncrono:

```python
async with TCPClient("192.168.50.1") as client:
    respuesta = await client.send_command(
        "LecturaUScmRaw"
    )
```

Al salir del bloque, la conexión TCP se cierra automáticamente.

Para el acceso local al hardware se utiliza un context manager síncrono:

```python
with USRotatingSensor() as sensor:
    sensor.setup()
    # Operaciones locales con el hardware
```

## 9. Limitaciones

Antes de utilizar el proyecto, deben tenerse en cuenta las siguientes limitaciones:

### 9.1. Hardware compatible
 
El acceso local al hardware está diseñado para ejecutarse en una Raspberry Pi compatible con GPIO Zero y un backend GPIO soportado por el sistema operativo.
 
La configuración validada utiliza:
 
```text
Raspberry Pi 4
Ubuntu 24.04.4 LTS
Python 3.12.3
GPIO Zero
LGPIO
```

La librería cliente `servoclient` puede utilizarse en Windows, Linux y macOS, pero no proporciona acceso directo a los GPIO. El control físico y del sensor ultrasónico se realiza exclusivamente en la Raspberry Pi que ejecuta el servidor.

### 9.2. Precisión del sensor ultrasónico

La precisión de las medidas depende de las características y limitaciones del sensor ultrasónico utilizado.

Las lecturas pueden verse afectadas por:

* Superficies blandas o absorbentes.
* Objetos pequeños o irregulares.
* Superficies situadas con una inclinación elevada respecto al sensor.
* Reflexiones múltiples del sonido.
* Interferencias producidas por otros sensores ultrasónicos.
* Objetos situados fuera del rango de medida.

Cuando el sensor no recibe un eco válido, puede devolver la distancia máxima configurada. En la configuración actual:

```text
MAX_DISTANCE_M = 2.0
```

Esto puede producir lecturas de:

```text
200 cm
```

Una lectura aislada de 200 cm no implica necesariamente un fallo del sensor. Si todas las lecturas devuelven ese valor, debe revisarse el cableado, la alimentación y la orientación del HC-SR04.

### 9.3. Precisión del barrido

El barrido realizado mediante el servomotor no equivale a un sistema de medición angular de alta precisión.

La precisión depende de:

* La calidad y tolerancia mecánica del servomotor.
* La correcta fijación del sensor al brazo del servo.
* El rango de pulsos PWM configurado.
* La alimentación eléctrica.
* Las holguras mecánicas del soporte.
* El tiempo de estabilización utilizado después de cada movimiento.

El proyecto está orientado a detección básica de obstáculos, prácticas docentes y prototipado. No está diseñado para realizar cartografía de alta precisión.

### 9.4. Liberación de la señal PWM

El servidor libera la señal PWM después de determinados movimientos para evitar microtemblores del servomotor durante los periodos de reposo.

Al liberar la señal PWM, el servo deja de mantener activamente la posición. Una fuerza externa, la gravedad o la carga mecánica pueden modificar ligeramente el ángulo alcanzado.

Este comportamiento debe tenerse en cuenta si la aplicación necesita mantener una posición bajo carga de forma continua.

### 9.5. Velocidad de adquisición

La velocidad de un barrido depende de:

* El número de posiciones angulares.
* El incremento configurado mediante salto_angulo.
* La distancia que debe recorrer el servomotor.
* El tiempo de estabilización mecánica.
* El número de muestras utilizadas en la lectura filtrada.
* La latencia de la conexión TCP.

Un incremento angular pequeño proporciona más medidas, pero aumenta el tiempo necesario para completar el barrido.

### 9.6. Dependencia de la red

En modo remoto, el rendimiento depende de la conexión entre la aplicación cliente y la Raspberry Pi.

Una red congestionada, una configuración IP incorrecta o la pérdida de conectividad pueden provocar:

* Aumento de la latencia.
* Tiempos de espera agotados.
* Interrupción de las operaciones.
* Pérdida de la conexión TCP.

Para tareas de mantenimiento puede utilizarse una conexión Ethernet directa con una dirección fija, por ejemplo:

```text
Raspberry Pi: 192.168.50.1/24
Ordenador:    192.168.50.2/24
```

### 9.7. Acceso concurrente

El servidor puede aceptar conexiones remotas, pero no implementa un sistema avanzado de reserva, planificación o exclusión del hardware entre varios usuarios.

Si varios clientes envían comandos simultáneamente, pueden producirse situaciones como:

* Órdenes de movimiento consecutivas o contradictorias.
* Barridos interrumpidos por otras peticiones.
* Lecturas realizadas mientras el servomotor está cambiando de posición.
* Resultados difíciles de asociar a una única práctica.

Cuando varios estudiantes comparten el mismo dispositivo, el acceso debe coordinarse desde la aplicación docente o mediante mecanismos adicionales de control.

### 9.8. Validación de parámetros

El servidor valida determinados parámetros, como el rango angular del servomotor. Sin embargo, la API no sustituye la validación que debe realizar la aplicación cliente.

Se recomienda comprobar antes de enviar una petición:

* Que el ángulo esté dentro del rango permitido.
* Que salto_angulo sea mayor que cero y que su signo sea coherente con el sentido del barrido.
* Que el ángulo inicial y final definan un barrido válido.
* Que el tiempo de espera sea adecuado para la operación solicitada.

### 9.9. Compatibilidad de la API

 La versión 1.0.0 proporciona la clase:

 ```python
from servoclient import TCPClient
 ```

 y el método genérico:

 ```python
await client.send_command(command, params)
 ```

Los nombres de los comandos TCP forman parte del protocolo compartido con el servidor. Una modificación incompatible de esos nombres o de la estructura de las respuestas puede requerir actualizar conjuntamente el cliente y el servidor.

Se recomienda utilizar versiones compatibles de ambos componentes.

### 9.10. Entornos críticos

El proyecto está orientado a:

* Docencia.
* Prácticas de laboratorio.
* Prototipado rápido.
* Experimentación con robótica móvil.

No ha sido diseñado ni certificado para:

* Aplicaciones industriales.
* Sistemas de seguridad.
* Operaciones críticas.
* Entornos en los que un error de medida o movimiento pueda producir daños.

## 10. Licencia

Este proyecto se distribuye bajo los términos de la licencia MIT.

Se permite su uso, copia, modificación y distribución, tanto para fines educativos como de investigación, de acuerdo con las condiciones establecidas en dicha licencia.

Consulte el archivo `LICENSE` para obtener el texto completo de la licencia.
# <span style="color: #FF5733;">Troubleshooting</span>

Este documento recopila los problemas más habituales detectados durante la instalación, configuración y operación de `servo-us-tcp-client`, junto con sus posibles soluciones.

# <span style="color: #71f489;">1. Cliente TCP</span>

## <span style="color: #ffbe33;">1.1. El cliente no puede conectar con el servidor</span>

### Síntoma

```text
OSError: [Errno 113] Connect call failed
```

<figure><center>
    <img src="../docs/images/troubleshooting/Errno113.png" alt="[OSError: Errno 113]" width="600">
</center></figure>

### Posibles causas

- La dirección IP configurada en `config.ini` es incorrecta.
- La Raspberry Pi no está conectada a la red
- El servidor TCP no está en ejecución.
- El puerto TCP 5050 no está accesible.
- Existe un cortafuegos bloqueando la comunicación.

### Verificaciones

Comprobar la ip configurada en `config.ini`:

```bash
cat config.ini
```

Comprobar el puerto TCP:

```bash
ss -tlnp | grep 5050
```

```bash
nc -vz IP_SERVIDOR 5050
```

Comprobar el estado del servidor:
```bash
sudo systemctl status servo-us-server.service
```

## <span style="color: #ffbe33;">1.2. Error al resolver la dirección del servidor</span>

### Síntoma

```text
socket.gaierror: [Errno -2] Name or service not known
```
<figure><center>
    <img src="../docs/images/troubleshooting/Errno-2.png" alt="[OSError: Errno 113]" width="600">
</center></figure>

### Causa

Configuración incorrecta en `config.ini`.

* Hostname inexistente.
* IP mal escrita.
* Caracteres extraños.
* Comillas mal puestas.

Incorrecto:

```ini
[server]
host = "10.10.12.169"
port = 5050
```

Correcto:

```ini
[server]
host = 10.10.12.169
port = 5050
```

## <span style="color: #ffbe33;">1.3. El cliente utiliza una IP incorrecta</span>

### Verificación

```bash
cat config.ini
```

### Solución

```ini
[server]
host = IP_DE_LA_RASPBERRY
port = 5050
```

# <span style="color: #71f489;">2. Servidor TCP</span>

## <span style="color: #ffbe33;">2.1. El servidor entra en bucle de reinicio</span>

### Síntoma:

<figure><center>
    <img src="../docs/images/troubleshooting/Server_no_arranca_error1.png" alt="[OSError: Errno 113]" width="800">
</center></figure>

### Causa:

La ruta definida en ExecStart apunta a un fichero inexistente, por lo tanto `Python` no puede localizar el script, `systemd` intenta reiniciarlo y el servicio entra en auto-restart automáticamente.

### Verificación

* Comprobar el estado

```bash
sudo systemctl status servo-us-server.service
```

* Consultar los registros:

```bash
sudo journalctl -u servo-us-server.service -n 50
```

* Verificar que el fichero existe

```bash
ls -l /home/create3_5/servo-us-tcp-client/server/
```

### Solución:

Editar el servicio:

```bash
sudo nano /etc/systemd/system/servo-us-server.service
```

Corregir la linea del `ExecStart`:

```bash
ExecStart=/home/create3_5/servo-us-tcp-client/.venv/bin/python3 -u /home/create3_5/servo-us-tcp-client/server/tcp_server.py
```

Recargar `systemd`

```bash
sudo systemctl daemon-reload
```

Reiniciar el servicio

```bash
sudo systemctl restart servo-us-server.service
```

Comprobar el correcto funcionamiento

```bash
sudo systemctl status servo-us-server.service
```

<figure><center>
    <img src="../docs/images/troubleshooting/Server_arrancado.png" alt="[activating server: -2]" width="800">
</center></figure>

## <span style="color: #ffbe33;">2.2. El servicio no encuentra el entorno virtual</span>

### Síntoma

<figure><center>
    <img src="../docs/images/troubleshooting/Server_no_arranca_error2.png" alt="[activating server: Errno 203]" width="800">
</center></figure>


### Causa

El fallo se produce porque el intérprete de Python definido en el `ExecStart` del servicio no existe. Es un error muy comun cuyas causas más comunes son:

* Se borra la carpeta .venv
* Se mueve el proyecto de ubicación
* Se reinstala Python
* Se restaura una copia incompleta del repositorio.

### Verificación

Comprobar el estado del servicio:

```bash
sudo systemctl status servo-us-server.service
```

Comprobar que existe el intérprete:

```bash
ls -l /home/create3_5/servo-us-tcp-client/.venv/bin/python3
```

### Solución

Editar el fichero de servicio:

```bash
sudo nano /etc/systemd/system/servo-us-server.service
```

Corregir la linea del `ExecStart`:

```bash
ExecStart=/home/create3_5/servo-us-tcp-client/.venv/bin/python3 -u /home/create3_5/servo-us-tcp-client/server/tcp_server.py
```

Recargar `systemd`

```bash
sudo systemctl daemon-reload
```

Reiniciar el servicio

```bash
sudo systemctl restart servo-us-server.service
```

Comprobar el correcto funcionamiento

```bash
sudo systemctl status servo-us-server.service
```

<figure><center>
    <img src="../docs/images/troubleshooting/Server_arrancado.png" alt="[activating server: -2]" width="800">
</center></figure>

## <span style="color: #ffbe33;">2.3. Error: No module named 'protocol'</span>

### Síntoma

<figure><center>
    <img src="../docs/images/troubleshooting/No-module-protocol.png" alt="[ModuleNotFoundError: No module named 'protocol']" width="800">
</center></figure>

### Causa

El archivo `common/protocol.py` no puede localizarse desde `server/tcp_server.py`

Esto suele ocurrir cuando:

* Se ha movido `protocol.py` a otra carpeta.
* Se ha eliminado o modificado el bloque `sys.path.append(...)`
* La estructura del repositorio no coincide con la esperada.
* Se ejecuta el script desde una ubicación incorrecta

### Verificación

Comprobar que el fichero existe

```bash
ls -l common/protocol.py
```

Comprobar que `tcp_server.py` contiene:

```bash
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "common"
    )
)
```

Comprobar la estructura del repositorio

```bash
tree -L 2
```

Salida esperada

```text
servo-us-tcp-client/
├── client/
├── common/
│   └── protocol.py
├── server/
│   ├── tcp_server.py
│   └── us_rotating_sensor.py
└── ...
```

### Solución

Añadir o restaurar el bloque

```bash
sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "common"
    )
)
```

antes del `import`

```bash
from protocol import Request, Response, send_framed, recv_framed
```

Verificar posteriormente ejecutando

```python
python server/tcp_server.py
```
Si el problema está resuelto, el servidor debería continuar con la inicialización normal y mostrar:

```text
Servidor escuchando en ('0.0.0.0', 5050)
```

## <span style="color: #ffbe33;">2.4. Error: No module named 'server'</span>

### Síntoma

<figure><center>
    <img src="../docs/images/troubleshooting/No-module-server.png" alt="[ModuleNotFoundError: No module named 'server']" width="800">
</center></figure>

### Solución

Utilizar:

```python
from us_rotating_sensor import USRotatingSensor
```

en lugar de:

```python
from server.us_rotating_sensor import USRotatingSensor
```

## <span style="color: #ffbe33;">2.5. Error: GPIO Busy</span>

### Síntoma

<figure><center>
    <img src="../docs/images/troubleshooting/puerto-ya-en-uso.png" alt="['GPIO busy']" width="800">
</center></figure>

### Causa

Los pines `GPIO` utilizados por el proyecto ya están siendo usados por otra instancia del servidor o por otra aplicación

Esto puede ocurrir cuando:

* El servicio `servo-us-server.service` ya está ejecutándose.
* Se intenta lanzar una segunda instancia manualmente.
* Otra aplicación está utilizando `GPIO17`, `GPIO18` o `GPIO27`

### Verificación

Comprobar que el servicio ya está funcionando

```bash
sudo systemctl status servo-us-server.service
```

Comprobar procesos Python activos

```bash
ps aux | grep tcp_server.py
```

### Solución

Si el servidor ya está funcionando mediante `systemd`, no iniciar una segunda instancia manualmente.

Detener el servicio antes de realizar pruebas manuales.

```bash
sudo systemctl stop servo-us-server.service
```

o finalizar cualquier proceso que esté utilizando los `GPIO`.

# <span style="color: #71f489;">3. Sensor ultrasónico HC-SR04</span>

## <span style="color: #ffbe33;">3.1. El sensor devuelve siempre 200 cm.</span>

### Síntoma

Las funciones `LecturaUScmRaw()` o `LecturaUScm_Filtrada()` devuelven siempre `200` o durante un barrido aparecen múltiples lecturas de `200`, por ejemplo:

```text
[100, 98, 200, 144, 102, 200, 131, 163, 107, 106]
```

### Causa

En la configuración por defecto de la librería:

```bash
MAX_DISTANCE_M = 2.0
```
Por tanto, cuando el sensor no recibe un eco válido, GPIO Zero devuelve la distancia máxima configurada (`2.0 metros = 200 cm.`). Esto suele indicar que el sensor no está recibiendo correctamente la reflexión ultrasónica.

### Posibles soluciones

* El sensor no está conectado físicamente.
* No hay ningún objeto delante del sensor.
* El sensor está apuntando al vacío.
* Cableado incorrecto. 
* Problema en el pin `ECHO`, revisar cableado, conectores y divisor de tensión.
* Objeto con mala reflexión.
* Sensor defectuoso

> NOTA: Durante los barridos es normal que aparezca alguna lectura aislada de 200 cm debido a reflexiones deficientes o pérdidas puntuales del eco.

# <span style="color: #71f489;">4. Servomotor</span>

## <span style="color: #ffbe33;">4.1. El servo no gira</span>

Tanto el servidor como el cliente funcionan correctamente, además el comando se ejecuta, pero el hardware no responde, por lo que la respuesta de datos será parecida a:

<figure><center>
    <img src="../docs/images/troubleshooting/servo-no-gira.png" alt="[El servo no gira]" width="800">
</center></figure>

### Causas:

* Cable de señal desconectado.
* Alimentación ausente en el servomotor.
* Masa (GND) desconectada.
* Señal conectada a un `GPIO` incorrecto.
* Servomotor defectuoso.

### Solución

Verificar el cableado y repetir la prueba

```text
SIGNAL -> GPIO18
VCC    -> 5V
GND    -> GND
```
## <span style="color: #ffbe33;">4.2. El servo vibra constantemente</span>

### Posibles causas

- Alimentación inestable.
- Ruido eléctrico.
- Montaje mecánico incorrecto.

### Solución

Comprobar alimentación y fijación mecánica.

# <span style="color: #71f489;">5. GPIO / LGPIO</span>

## <span style="color: #ffbe33;">5.1. Error: Unable to load any default pin factory</span>

### Síntoma

Al arrancar el servidor aparece un error similar a:

```text
gpiozero.exc.BadPinFactory: Unable to load any default pin factory!
```
o

```text
RuntimeError: USRotatingSensor.setup: Fallo en inicialización de hardware: Unable to load any default pin factory!
```

### Causa

GPIO Zero no encuentra un backend GPIO válido. para acceder a los pines de la Raspberry Pi.

Este problema puede ocurrir cuando:

* No están instaladas las dependencias necesarias.
* El paquete `lgpio` no está disponible en el entorno virtual.
* GPIO Zero no puede inicializar ningún backend compatible.

En las pruebas realizadas sobre Ubuntu 24.04.4 LTS, GPIO Zero intentó utilizar sucesivamente:

```text
lgpio
RPi.GPIO
pigpio
native
```

sin encontrar ninguno disponible

### Verificación

Comprobar que `gpiozero` está instalado:

```bash
pip list | grep gpiozero
```

Comprbar que `lgpio` está disponible:

```bash
python -c "import lgpio; print('lgpio OK')"
```
Comprobar qué backend utiliza GPIO Zero:

```bash
python -c "from gpiozero import Device; Device.ensure_pin_factory(); print(Device.pin_factory)"
```
Salida esperada:

```text
<gpiozero.pins.lgpio.LGPIOFactory ...>
```

### Solución
 
Activar el entorno virtual:
 
```bash
source .venv/bin/activate
```
 
Instalar las dependencias:
 
```bash
pip install -r server/requirements.txt
```
 
Si fuera necesario:
 
```bash
pip install lgpio
```
 
Verificar nuevamente:
 
```bash
python -c "import lgpio; print('lgpio OK')"
```
 
Después iniciar el servidor:
 
```bash
python server/tcp_server.py
```
 
La salida esperada es:
 
```text
Servidor escuchando en ('0.0.0.0', 5050)
```

### Información adicional
 
Las primeras versiones del proyecto utilizaban `PiGPIOFactory()` lo que requería el servicio `pigpiod`.
 
Tras las pruebas realizadas sobre Ubuntu 24.04.4 LTS, el proyecto fue adaptado para utilizar el backend por defecto de GPIO Zero (`LGPIO`), eliminando la dependencia de `pigpiod` y simplificando considerablemente la instalación y mantenimiento del servidor.

## <span style="color: #ffbe33;">5.2. Error relacionado con PiGPIOFactory</span>

### Síntoma

```text
failed to connect to localhost:8888
```

### Causa

Dependencia de `pigpiod`.

### Solución adoptada en este proyecto

El proyecto utiliza el backend por defecto de GPIO Zero (`LGPIO`) y no requiere `pigpiod`.

# <span style="color: #71f489;">6. systemd</span>

## <span style="color: #ffbe33;">6.1. El servicio no existe</span>

### Síntoma

Al intentar consultar el estado del servicio aparece un mensaje similar a:

```text
Unit servo-us-server.service could not be found.
```

### Causa

El nombre del servicio es incorrecto o el fichero `.service` todavía no ha sido creado.

También puede ocurrir cuando:

* Se ha escrito mal el nombre del servicio.
* El fichero no existe en `/etc/systemd/system/`.
* El servicio fue eliminado accidentalmente.
* Se está utilizando un nombre antiguo que ya no coincide con el actual.

### Verificación

Listar los servicios relacionados:

```bash
ls /etc/systemd/system/ | grep servo
```
 
Consultar el estado del servicio correcto:
 
```bash
sudo systemctl status servo-us-server.service
```
 
Verificar que el fichero existe:
 
```bash
ls -l /etc/systemd/system/servo-us-server.service
```

### Solución

Si el servicio existe pero se está utilizando un nombre incorrecto, utilizar el nombre correcto:

```bash
sudo systemctl status servo-us-server.service
```

Si el fichero no existe, recrearlo siguiendo las instrucciones descritas en [Laboratory Setup](../docs/laboratory-setup.md).

Una vez creado:

```bash
sudo systemctl daemon-reload
```
 
```bash
sudo systemctl enable servo-us-server.service
```
 
```bash
sudo systemctl start servo-us-server.service
```

### Comprobación

```bash
sudo systemctl status servo-us-server.service
```
 
Salida esperada:
 
```text
Loaded: loaded (/etc/systemd/system/servo-us-server.service; enabled)
Active: active (running)
```

## <span style="color: #ffbe33;">6.2. El servicio no arranca</span>

### Síntoma

Al consultar el estado del servicio aparece:

```text
Active: failed
```

o

```text
Active: activating (auto-restart) (Result: exit-code)
```

También pueden aparecer mensajes como:

```text
code=exited, status=1/FAILURE
```

o:

```text
code=exited, status=2
```

### Posibles causas

- Error de sintaxis en el código Python.
- Dependencias no instaladas.
- Ruta incorrecta en `ExecStart`.
- Entorno virtual inexistente.
- Error durante la inicialización del hardware.
- Puerto TCP ocupado.
- Configuración incorrecta del servicio systemd.

### Verificación

Comprobar el estado del servicio:

```bash
sudo systemctl status servo-us-server.service
```

Consultar los registros:

```bash
sudo journalctl -u servo-us-server.service -n 50
```

Consultar los registros en tiempo real:

```bash
sudo journalctl -u servo-us-server.service -f
```

### Diagnóstico rápido

Intentar arrancar el servidor manualmente:

```bash
cd ~/servo-us-tcp-client

source .venv/bin/activate

python server/tcp_server.py
```

Si el servidor falla también de forma manual, el problema se encuentra en el código, las dependencias o el hardware.

Si el servidor funciona manualmente pero no mediante systemd, revisar:

```ini
WorkingDirectory=
ExecStart=
```

del fichero:

```bash
sudo systemctl cat servo-us-server.service
```

### Solución

Identificar primero el error real utilizando:

```bash
sudo journalctl -u servo-us-server.service -n 100
```

y corregir la causa raíz.

Una vez realizada la corrección:

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl restart servo-us-server.service
```

Verificar:

```bash
sudo systemctl status servo-us-server.service
```

La salida esperada es:

```text
Loaded: loaded (/etc/systemd/system/servo-us-server.service; enabled)

Active: active (running)
```

## <span style="color: #ffbe33;">6.3. El servicio entra en bucle de reinicio</span>

### Síntoma

Al consultar el estado del servicio aparece un mensaje similar a:

```text
Active: activating (auto-restart) (Result: exit-code)
```

También pueden aparecer mensajes como:

```text
Scheduled restart job, restart counter is at 83
```

o:

```text
code=exited, status=1/FAILURE
```

```text
code=exited, status=2
```

```text
status=203/EXEC
```

### Causa

El servicio intenta arrancar, pero encuentra un error durante la inicialización y finaliza.

Debido a la configuración:

```ini
Restart=on-failure
```

systemd intenta reiniciarlo automáticamente, produciendo un ciclo de reinicios continuos.

### Posibles causas

- Ruta incorrecta en `ExecStart`.
- Entorno virtual inexistente.
- Dependencias Python no instaladas.
- Error de sintaxis en el código.
- Hardware desconectado.
- GPIO ocupados por otra instancia.
- Puerto TCP ya utilizado por otro proceso.
- Fichero de configuración incorrecto.

### Verificación

Consultar el estado:

```bash
sudo systemctl status servo-us-server.service
```

Consultar los registros:

```bash
sudo journalctl -u servo-us-server.service -n 100
```

Seguimiento en tiempo real:

```bash
sudo journalctl -u servo-us-server.service -f
```

### Diagnóstico rápido

Intentar arrancar manualmente el servidor:

```bash
cd ~/servo-us-tcp-client

source .venv/bin/activate

python server/tcp_server.py
```

Si el error aparece también en modo manual, la causa no está en systemd sino en el propio servidor o en sus dependencias.

### Solución

Identificar primero el error real que provoca la finalización del proceso.

Una vez corregido:

```bash
sudo systemctl daemon-reload
```

```bash
sudo systemctl restart servo-us-server.service
```

Comprobar:

```bash
sudo systemctl status servo-us-server.service
```

La salida esperada es:

```text
Active: active (running)
```

### Información adicional

El reinicio automático es un comportamiento esperado y deseable, ya que permite que el servicio vuelva a ponerse en marcha automáticamente cuando el problema haya sido corregido sin necesidad de reiniciar la Raspberry Pi.

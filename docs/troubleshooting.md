# Troubleshooting

Este documento recopila los problemas más habituales detectados durante la instalación, configuración y operación de `servo-us-tcp-client`, junto con sus posibles soluciones.

# Cliente TCP

## El cliente no puede conectar con el servidor

### Síntoma

```text
ConnectionRefusedError: [Errno 111] Connect call failed
```

### Posibles causas

- El servidor TCP no está en ejecución.
- La dirección IP configurada en `config.ini` es incorrecta.
- El puerto TCP 5050 no está accesible.
- Existe un cortafuegos bloqueando la comunicación.

### Verificaciones

```bash
sudo systemctl status servo-us-server.service
```

```bash
ss -tlnp | grep 5050
```

```bash
nc -vz IP_SERVIDOR 5050
```


## Error al resolver la dirección del servidor

### Síntoma

```text
socket.gaierror: [Errno -2] Name or service not known
```

### Causa

Configuración incorrecta en `config.ini`.

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

## El cliente utiliza una IP incorrecta

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

# Servidor TCP

## El servidor no arranca

### Verificación

```bash
source .venv/bin/activate
python server/tcp_server.py
```

Leer el error completo mostrado por consola.

## Error: No module named 'protocol'

### Causa

`protocol.py` fue movido a:

```text
common/protocol.py
```

### Solución

Comprobar que `tcp_server.py` y `tcp_client.py` añaden correctamente la carpeta `common` al `sys.path`.

## Error: No module named 'server'

### Síntoma

```text
ModuleNotFoundError: No module named 'server'
```

### Solución

Utilizar:

```python
from us_rotating_sensor import USRotatingSensor
```

en lugar de:

```python
from server.us_rotating_sensor import USRotatingSensor
```

## El puerto 5050 ya está en uso

### Síntoma

```text
Address already in use
```

### Verificación

```bash
ss -tlnp | grep 5050
```

### Solución

Identificar el proceso responsable:

```bash
sudo lsof -i :5050
```

# Sensor ultrasónico HC-SR04

## El sensor devuelve siempre 200 cm

### Posibles causas

- Sensor desconectado.
- Cableado incorrecto.
- Pin ECHO mal conectado.
- Distancia fuera del rango de medida.

### Verificaciones

```text
TRIG -> GPIO17
ECHO -> GPIO27
VCC  -> 5V
GND  -> GND
```

## Lecturas erráticas o inestables

### Posibles causas

- Divisor resistivo incorrecto.
- Mala alimentación.
- Reflexiones múltiples.
- Sensor mal fijado.

### Divisor de tensión recomendado

```text
R1 = 1 kΩ
R2 = 2 kΩ
```

## El sensor no responde

### Comprobación básica

Ejecutar:

```bash
python client/tcp_client.py
```

Si las llamadas a `LecturaUScmRaw()` o `LecturaUScm_Filtrada()` fallan, revisar el cableado.

# Servomotor

## El servo no gira

### Verificaciones

```text
SIGNAL -> GPIO18
VCC    -> 5V
GND    -> GND
```

### Posibles causas

- Alimentación insuficiente.
- Masa común desconectada.
- Error de cableado.

## El servo vibra constantemente

### Posibles causas

- Alimentación inestable.
- Ruido eléctrico.
- Montaje mecánico incorrecto.

### Solución

Comprobar alimentación y fijación mecánica.

# GPIO / LGPIO

## Error: Unable to load any default pin factory

### Síntoma

```text
gpiozero.exc.BadPinFactory: Unable to load any default pin factory!
```

### Causa

GPIO Zero no encuentra un backend GPIO válido.

### Verificación

```bash
python -c "import lgpio; print('lgpio OK')"
```

### Solución

Instalar dependencias:

```bash
pip install -r server/requirements.txt
```

## Error relacionado con PiGPIOFactory

### Síntoma

```text
failed to connect to localhost:8888
```

### Causa

Dependencia de `pigpiod`.

### Solución adoptada en este proyecto

El proyecto utiliza el backend por defecto de GPIO Zero (`LGPIO`) y no requiere `pigpiod`.

# systemd

## El servicio no existe

### Síntoma

```text
Unit servo-us-server.service could not be found.
```

### Verificación

```bash
ls /etc/systemd/system/ | grep servo
```

## El servicio no arranca

### Verificación

```bash
sudo systemctl status servo-us-server.service
```

```bash
sudo journalctl -u servo-us-server.service -n 50
```

## El servicio entra en bucle de reinicio

### Síntoma

```text
Active: activating (auto-restart)
```

### Posibles causas

- Hardware desconectado.
- Puerto ocupado.
- Error de Python.
- Dependencias ausentes.

## Se modifica el fichero .service y los cambios no tienen efecto

### Solución

```bash
sudo systemctl daemon-reload
sudo systemctl restart servo-us-server.service
```

## El servicio arranca manualmente pero no mediante systemd

### Verificación

```bash
sudo systemctl cat servo-us-server.service
```

Comprobar:

```ini
WorkingDirectory=
ExecStart=
```

# Red

## El puerto TCP no es accesible desde otro equipo

### Verificación

```bash
nc -vz IP_SERVIDOR 5050
```

```bash
ss -tlnp | grep 5050
```

### Posibles causas

- Servicio detenido.
- Firewall.
- Dirección IP incorrecta.
- Problemas de red.

# Comprobación rápida del sistema

## Estado del servicio

```bash
sudo systemctl status servo-us-server.service
```

## Puerto TCP

```bash
ss -tlnp | grep 5050
```

## Cliente

```bash
python client/tcp_client.py
```

## Arranque automático

```bash
sudo systemctl is-enabled servo-us-server.service
```

Salida esperada:

```text
enabled
```

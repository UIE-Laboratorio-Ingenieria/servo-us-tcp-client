# Server

Servidor TCP para el control remoto de un sensor de ultrasonidos montado sobre un servomotor conectado a una Raspberry Pi.

Este componente forma parte del proyecto `servo-us-tcp-client` y proporciona acceso remoto al hardware mediante una arquitectura cliente-servidor basada en TCP.

## Objetivo

El servidor permite exponer remotamente las funcionalidades de la clase `USRotatingSensor` a través de la red local.

Los clientes pueden:

* Mover el servomotor.
* Obtener lecturas directas del sensor de ultrasonidos.
* Obtener lecturas filtradas.
* Realizar barridos angulares completos.
* Recibir los resultados mediante respuestas JSON.

## Requisitos

### Hardware

* Raspberry Pi 4 o superior
* Sensor de ultrasonidos HC-SR04 o compatible.
* Servomotor de 180º.
* Alimentación adecuada para el conjunto servo-sensor.
* Conectividad de red local

### Software

- Ubuntu 24.04 LTS o superior.
- Python 3.12 o superior.
- Entorno virtual Python.
- GPIO Zero.
- LGPIO.

## Instalación

### Clonar el repositorio

```bash
git clone https://github.com/UIE-Laboratorio-Ingenieria/servo-us-tcp-client.git
cd servo-us-tcp-client
```

### Crear entorno virtual y activarlo

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Instalar dependencias

```bash
pip install --upgrade pip
pip install -r server/requirements.txt
```

## Conexiones hardware

### Sensor de ultrasonidos HC-SR04

| Sensor | GPIO Raspberry Pi |
|--------|-------------------|
| TRIG | GPIO 17 |
| ECHO | GPIO 27 |
| VCC | 5V |
| GND | GND |

> IMPORTANTE: El pin ECHO del HC-SR04 trabaja a 5V. Debe utilizarse un divisor de tensión o un adaptador de nivel lógico antes de conectarlo a la Raspberry Pi.

### Servomotor

| Señal | GPIO Raspberry Pi |
|--------|--------|
| Control PWM | GPIO 18 |
| VCC | 5V |
| GND | GND |
 
## Arquitectura

```text
                     Cliente TCP
                         │
                         ▼
                +-------------------+
                |   tcp_server.py   |
                +-------------------+
                         │
                         ▼
                +-------------------+
                |  USRotatingSensor |
                +-------------------+
                    │          │
                    ▼          ▼
                  Servo     HC-SR04
```

## Arranque manual

Iniciar el servidor:

```bash
source .venv/bin/activate
python server/tcp_server.py
```

Salida esperada:

```text
Servidor escuchando en ('0.0.0.0', 5050)
```

### Despliegue como servicio `systemd`

Crear el fichero:

```bash
sudo nano /etc/systemd/system/servo-us-server.service
```

Contenido:

```ini
[Unit]
Description=Servo Ultrasonic TCP Server
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=create3_5
WorkingDirectory=/home/create3_5/servo-us-tcp-client
ExecStart=/home/create3_5/servo-us-tcp-client/.venv/bin/python3 -u /home/create3_5/servo-us-tcp-client/server/tcp_server.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
[Install]
WantedBy=multi-user.target
```

Recargar `systemd`

```bash
sudo systemctl daemon-reload
```

Habilitar el servicio:

```bash
sudo systemctl enable servo-us-server.service
```

Iniciar el servicio:

```bash
sudo systemctl start servo-us-server.service
```

Verificar:

```bash
sudo systemctl status servo-us-server.service
```

## Puerto utilizado

Por defecto:

```text
TCP 5050
```

Asegúrese de que el puerto está accesible desde los equipos del cliente.

Verificación:

```bash
ss -tlnp | grep 5050
```

## Comandos soportados

### *gira_servo_raw*

Mueve el servomotor al ángulo especificado.

Parámetros:

```json
{
    "angle": 90
}
```

### **gira_servo**

Mueve el servomotor y espera el tiempo necesario para completar el movimiento.

Parámetros:

```json
{
    "angle": 180
}
```

### **LecturaUScm_Filtrada**

Obtiene una lectura filtrada utilizando múltiples muestras.

Parámetros:
1
```json
{}
```

### **realizar_barrido**
 
Realiza un barrido angular completo.

Parámetros:

```json
{
    "ang_inicio": 0,
    "ang_fin": 180,
    "salto_angulo": 20,
    "retorno_final": true
}
```

## Resolución de problemas

### El servidor no arranca

Comprobar:

```bash
python server/tcp_server.py
```

y revisar el mensaje de error mostrado.

### El puerto 5050 no está disponible

Verificar:

```bash
ss -tlnp | grep 5050
```

### El servo no responde

Comprobar:

- Alimentación del servo.
- Conexión a GPIO18.
- Masa compartida con la Raspberry Pi.

### El sensor devuelve siempre 200 cm

Comprobar:

- Cableado TRIG/ECHO.
- Divisor de tensión del pin ECHO.
- Distancia máxima configurada.
- Alimentación del sensor.

### Las medidas son inestables

Comprobar
- Calidad de la alimentación.
- Interferencias mecánicas del servomotor.
- Correcta fijación del sensor ultrasónico.

## Entorno validado

Este servidor ha sido probado con:

```text
Ubuntu 24.04.4 LTS
Python 3.12.3
GPIO Zero
LGPIO
```

## Licencia

Consulte el archivo `LICENSE` situado en la raíz del proyecto.
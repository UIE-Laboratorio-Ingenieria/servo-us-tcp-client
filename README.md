# servo-ir-tcp-client

## 1. Objetivo

Proporciona uns forma simple y directa para el control de un sensor ultrasónico montado sobre un servomotor conectado a una Raspberry Pi, permitiendo realizar mediciones de distancia y barridos angulares desde aplicaciones Python.

La librería está orientada principalmente a docencia, prácticas de laboratorio y prototipado rápido de aplicaciones de robótica móvil y sensorización, ofreciendo una API senscilla basada en Python asíncrono.

Además de la ejecución local sobre la Raspberry Pi, el proyecto incluye una arquitectura cliente-servidor basada en TCP que permite acceder remotamente al hardware desde cualquier ordenador de la misma red, facilitando el desarrollo distribuido y el acceso compartido a los dispositivos del laboratorio.

Los principales casos de uso son:

* Medición de distancias mediante sensores ultrasónicos.
* Realización de barrido angulares para detección de obstáculos.
* Generación de mapas unidimensionales del entorno.
* Prácticas docente de programación asíncrona con Python.
* Acceso remoto a hardware conectado a Raspberry Pi mediante sockets TCP.
* Proyectos de robótica móvil y navegación basada en sensores de distancia.

## 2. Características

* Control de un servo de 180º mediante Raspberry Pi y GPIO Zero.
* Lectura de distancias utilizando sensores ultrasónicos compatibles con HC-SR04 o similares.
* Medición directa de distancia en centímetros.
* Filtrado automático de lecturas para reducir el efecto de valores espúrios.
* Realización de barridos angulares configurables.
* API basada en programación asíncrona mediante asyncio.
* Gestión automática de recursos hardware mediante context managers.
* Registro opcional de actividad mediante ficheros de log.
* Arquitectura cliente-servidor basada en TCP.
* Acceso remoto al hardware desde cualquier equipo de la misma red.
* Protocolo de comunicación sencillo basado en mensajes JSON.
* Orientado a la docencia, prácticas de laboratorio y prototipado rápido de aplicaciones de robótica.
* 
## 3. Instalación
## 4. Configuración Raspberry Pi
## 5. Quick Start
## 6. Arquitectura Cliente-Servidor
## 7. API
## 8. Ejemplos
## 9. Limitaciones
## 10. Licencia
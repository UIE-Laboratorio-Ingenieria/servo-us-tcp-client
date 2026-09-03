# Changelog

Todas las modificaciones relevantes de este proyecto se documentarán en este archivo.

Este proyecto sigue las recomendaciones de [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y utiliza versionado semántico siempre que sea posible.

## [1.0.0] - 2026-09-03

### Added

- Implementación de la clase `USRotatingSensor`.
- Control de servomotores mediante GPIO Zero.
- Lectura de sensores de ultrasonidos compatibles con HC-SR04.
- Lectura directa de distancias mediante `LecturaUScmRaw()`.
- Filtrado de medidas mediante `LecturaUScm_Filtrada()`.
- Realización de barridos angulares configurables.
- Gestión automática de recursos hardware mediante context managers.
- Sistema de registro de actividad mediante ficheros de log.
- Arquitectura cliente-servidor basada en TCP.
- Cliente TCP para acceso remoto al hardware.
- Servidor TCP para control de dispositivos conectados a Raspberry Pi.
- Protocolo de comunicación JSON sobre TCP.
- Ejemplos de uso local y remoto.
- Documentación inicial del proyecto.
- Licencia MIT.

### Changed

- Refactorización de nombres internos para mejorar la legibilidad del código.
- Mejora de comentarios y documentación interna.

### Fixed

- Corrección de errores en la liberación de recursos hardware.
- Mejora de la gestión de excepciones durante la inicialización y cierre de dispositivos.
- Mejora de la estabilidad en lecturas del sensor ultrasónico mediante filtrado estadístico.
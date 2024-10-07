# Arquitectura del Sistema

## Componentes
- **Cliente**: Interfaz de línea de comandos para subir, descargar, listar y eliminar archivos.
- **Servidor**: Gestiona las solicitudes de múltiples clientes concurrentemente.
- **Sistema de Almacenamiento**: Almacenamiento local de archivos en el servidor.

## Comunicación y Concurrencia
- **Sockets**: Comunicación en tiempo real entre cliente y servidor.
- **Hilos**: Uso de `threading` para manejar conexiones concurrentes.
- **Asincronismo**: `AsyncIO` para gestionar operaciones de I/O no bloqueantes.
- **IPC**: Uso de colas o pipes (`queue.Queue`, `multiprocessing.Pipe`) para la coordinación interna entre procesos o hilos.

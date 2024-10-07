# Decisiones de Diseño

## Uso de Sockets
Se eligió el uso de sockets para permitir la comunicación en tiempo real entre los clientes y el servidor. Este enfoque es adecuado para aplicaciones cliente-servidor.

## Concurrencia con Hilos y AsyncIO
El servidor maneja múltiples conexiones usando hilos, cada cliente es gestionado en un hilo separado. Además, se utiliza `AsyncIO` para operaciones de entrada/salida, lo que permite que el servidor maneje múltiples operaciones sin bloquearse.

## IPC para Modularidad
El uso de colas o pipes permite dividir el procesamiento de archivos en diferentes componentes o procesos, mejorando la escalabilidad y modularidad del sistema.

## Posibles Expansiones
- Implementación de una cola de tareas distribuidas para gestionar la subida y descarga de archivos de manera más eficiente.
- Agregar una base de datos para almacenar metadata de los archivos.

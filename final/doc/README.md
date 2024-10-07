# Aplicación de Almacenamiento en la Nube

## Descripción General
La aplicación es un sistema cliente-servidor que permite a los usuarios subir, descargar, listar y eliminar archivos de manera concurrente desde cualquier lugar con acceso a Internet. El sistema utiliza sockets para la comunicación entre clientes y servidor, y aprovecha la concurrencia y asincronismo para gestionar múltiples conexiones y operaciones de entrada/salida.

## Funcionalidades
- **Subida de archivos**: El cliente puede subir archivos al servidor.
- **Descarga de archivos**: Los clientes pueden descargar archivos disponibles.
- **Gestión de archivos**: Listado y eliminación de archivos.
- **Concurrencia**: Uso de `AsyncIO` y `threading` para gestionar múltiples clientes de manera simultánea.

## Requisitos
- Python 3.8 o superior
- Bibliotecas: `asyncio`, `socket`, `argparse`

## Instalación
Consulta el archivo `INSTALL.md` para instrucciones detalladas sobre la instalación y configuración del entorno.

# server_asyncio.py
import asyncio
import multiprocessing

from file_worker import file_process_main  # Importamos la función del worker

# Creamos las colas de comunicación
request_queue = multiprocessing.Queue()
response_queue = multiprocessing.Queue()

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"[DEBUG] Cliente conectado: {addr}")

    try:
        # Leer la primera línea, por ejemplo "upload\n", "download file.txt\n", etc.
        data = await reader.readline()  
        if not data:
            # Cliente cerró la conexión
            writer.close()
            await writer.wait_closed()
            return
        
        line = data.decode().strip()  # p.ej.: "upload", "download file.txt"
        parts = line.split()
        operation = parts[0]  # "upload", "download", etc.

        if operation == "upload":
            await handle_upload_async(parts, reader, writer)

        elif operation == "download":
            await handle_download_async(parts, writer)

        elif operation == "delete":
            await handle_delete_async(parts, writer)

        elif operation == "list":
            await handle_list_async(writer)

        else:
            writer.write(b"Error: Comando inexistente\n")
            await writer.drain()

    except Exception as e:
        print(f"[DEBUG] Error en handle_client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"[DEBUG] Cliente desconectado: {addr}")


async def handle_upload_async(parts, reader, writer):
    """
    Espera la secuencia:
      1) START\n
      2) filename\n
      3) contenido hasta <END>
    Luego envía la petición (upload) al worker y espera la respuesta.
    """
    # 1) Leer 'START\n'
    start_line = await reader.readline()
    if start_line.strip() != b"START":
        writer.write(b"Error: falto START\n")
        await writer.drain()
        return

    # 2) Leer el nombre de archivo
    filename_line = await reader.readline()
    filename = filename_line.decode().strip()

    # 3) Leer el contenido hasta '<END>'
    content_buffer = b""
    while True:
        chunk = await reader.read(1024)
        if not chunk:
            # Se cerró conexión antes de <END>
            writer.write(b"Error: conexion cerrada inesperadamente\n")
            await writer.drain()
            return

        end_pos = chunk.find(b"<END>")
        if end_pos != -1:
            # Encontramos <END>, concatenamos lo anterior
            content_buffer += chunk[:end_pos]
            # Ignoramos lo que sigue de <END> en este chunk
            break
        else:
            content_buffer += chunk

    # Encolar la petición al worker
    request_queue.put(("upload", filename, content_buffer))
    # Esperar la respuesta
    result = response_queue.get()  # bloquea este hilo/corrutina hasta que llegue algo

    if result[0] == "ok":
        writer.write(f"{result[1]}\n".encode())  # Mensaje de éxito
    else:
        writer.write(f"Error: {result[1]}\n".encode())
    await writer.drain()


async def handle_download_async(parts, writer):
    """
    Espera "download filename", donde:
      parts[0] = "download"
      parts[1] = "filename"
    """
    if len(parts) < 2:
        writer.write(b"Error: falta nombre de archivo\n")
        await writer.drain()
        return

    filename = parts[1]

    # Encolar la petición
    request_queue.put(("download", filename))
    result = response_queue.get()

    if result[0] == "ok":
        file_content = result[1]  # bytes
        writer.write(file_content)
        await writer.drain()
        # Al final, enviamos 'EOF' para indicar fin
        writer.write(b"EOF")
        await writer.drain()
    else:
        writer.write(f"Error: {result[1]}\n".encode())
        await writer.drain()


async def handle_delete_async(parts, writer):
    """
    Espera "delete filename"
    """
    if len(parts) < 2:
        writer.write(b"Error: falta nombre de archivo\n")
        await writer.drain()
        return

    filename = parts[1]
    request_queue.put(("delete", filename))
    result = response_queue.get()

    if result[0] == "ok":
        writer.write(f"{result[1]}\n".encode())
    else:
        writer.write(f"Error: {result[1]}\n".encode())
    await writer.drain()


async def handle_list_async(writer):
    request_queue.put(("list", None))
    result = response_queue.get()

    if result[0] == "ok":
        file_list = result[1]  # lista de archivos
        if not file_list:
            writer.write(b"No se encontraron archivos\n")
        else:
            writer.write(("\n".join(file_list) + "\n").encode())
    else:
        writer.write(f"Error: {result[1]}\n".encode())
    await writer.drain()


async def main_server(port=8080):
    server = await asyncio.start_server(
        handle_client,
        "0.0.0.0",  # Aceptar conexiones de cualquier interfaz
        port
    )
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"[DEBUG] Servidor corriendo en {addrs}")
    async with server:
        await server.serve_forever()


def run_server_asyncio():
    # 1) Iniciar el proceso worker
    worker_process = multiprocessing.Process(
        target=file_process_main,
        args=(request_queue, response_queue)
    )
    worker_process.start()

    # 2) Iniciar el bucle asyncio
    try:
        asyncio.run(main_server(8080))
    except KeyboardInterrupt:
        print("[DEBUG] Deteniendo servidor...")

    # 3) Al terminar, avisamos al worker que acabe
    request_queue.put(None)
    worker_process.join()


if __name__ == "__main__":
    run_server_asyncio()

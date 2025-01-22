import asyncio
import multiprocessing
from celery_app import upload_file, download_file, delete_file, list_files

from file_worker import file_process_main  # Importamos la función del worker

HOST = "0.0.0.0"
PORT = 8080

#la mayoria de los comentarios fue del inicio del proyecto antes de implementar colas
#request_queue = multiprocessing.Queue()
#response_queue = multiprocessing.Queue()

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"[DEBUG] Cliente conectado: {addr}")

    try:
        #leo la primera línea, por ejemplo "upload\n", "download file.txt\n", etc.
        data = await reader.readline()  
        if not data:
            #cierro la conexion del cliente
            writer.close()
            await writer.wait_closed()
            return
        
        line = data.decode().strip()  # "upload", "download file.txt"
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
    #leo 'START\n'
    start_line = await reader.readline()
    if start_line.strip() != b"START":
        writer.write(b"Error: falto START\n")
        await writer.drain()
        return

    #leo el nombre de archivo
    filename_line = await reader.readline()
    filename = filename_line.decode().strip()

    username_line = await reader.readline()
    username = username_line.decode().strip()

    #leo el contenido hasta '<END>'
    content_buffer = b""
    while True:
        chunk = await reader.read(1024)
        if not chunk:
            #se cierra conexión antes de <END>
            writer.write(b"Error: conexion cerrada inesperadamente\n")
            await writer.drain()
            return

        end_pos = chunk.find(b"<END>")
        if end_pos != -1:
            #lee <END>, concatenamos lo anterior
            content_buffer += chunk[:end_pos]
            break
        else:
            content_buffer += chunk

    #encola la petición al worker
    #request_queue.put(("upload", filename, content_buffer))
    #llamo a celery
    result_async = upload_file.delay(filename, content_buffer, username)
    result = result_async.get()

    #espera la respuesta
    writer.write(f"{result}\n".encode())
    await writer.drain()
    #result = response_queue.get()  # bloquea este hilo/corrutina hasta que llegue algo

    #if result[0] == "ok":
    #    writer.write(f"{result[1]}\n".encode())  # Mensaje de éxito
    #else:
    #    writer.write(f"Error: {result[1]}\n".encode())
    #await writer.drain()


async def handle_download_async(parts, writer):
    filename = parts[1]
    result_async = download_file.delay(filename)
    res = result_async.get()
    
    if isinstance(res, str) and res.startswith("Error:"):
        writer.write(res.encode())
        await writer.drain()
        return
    else:
        writer.write(res)
        writer.write(b"EOF")
        await writer.drain()

    #encola la petición
    #request_queue.put(("download", filename))
    #result = response_queue.get()

    #if result[0] == "ok":
    #    file_content = result[1]  # bytes
    #    writer.write(file_content)
    #    await writer.drain()
        # Al final, enviamos 'EOF' para indicar fin
    #    writer.write(b"EOF")
    #    await writer.drain()
    #else:
    #    writer.write(f"Error: {result[1]}\n".encode())
    #    await writer.drain()


async def handle_delete_async(parts, writer):
    if len(parts) < 2:
        writer.write(b"Error: falta nombre de archivo\n")
        await writer.drain()
        return

    filename = parts[1]
    result_async = delete_file.delay(filename)
    message = result_async.get()
    writer.write(f"{message}\n".encode())
    await writer.drain()

    #request_queue.put(("delete", filename))
    #result = response_queue.get()

    #if result[0] == "ok":
    #    writer.write(f"{result[1]}\n".encode())
    #else:
    #    writer.write(f"Error: {result[1]}\n".encode())
    #await writer.drain()


async def handle_list_async(writer):
    result_async = list_files.delay()
    data = result_async.get()
    if not data:
        writer.write(b"No se encontraron archivos\n")
    else:
        print("[DEBUG] list data repr:", repr(data))
        writer.write(data.encode())
        #writer.write(("\n".join(files) + "\n").encode())
    await writer.drain()

    #request_queue.put(("list", None))
    #result = response_queue.get()

    #if result[0] == "ok":
    #    file_list = result[1]  # lista de archivos
    #    if not file_list:
    #        writer.write(b"No se encontraron archivos\n")
    #    else:
    #        writer.write(("\n".join(file_list) + "\n").encode())
    #else:
    #    writer.write(f"Error: {result[1]}\n".encode())
    #await writer.drain()


async def main_server():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"[DEBUG] Servidor corriendo en {addrs}")
    async with server:
        await server.serve_forever()


def run_server_asyncio():
    #worker_process = multiprocessing.Process(
    #    target=file_process_main,
    #    args=(request_queue, response_queue)
    #)
    #worker_process.start()

    try:
        asyncio.run(main_server())
    except KeyboardInterrupt:
        print("[DEBUG] Deteniendo servidor...")

    #request_queue.put(None)
    #worker_process.join()


if __name__ == "__main__":
    run_server_asyncio()

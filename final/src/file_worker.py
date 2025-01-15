import os
import time
import multiprocessing

STORAGE_DIR = "/Users/gpersia/Documents/Facultad/proyecto_final_compu2/final/nube/Subidos"

def file_process_main(request_queue, response_queue):
    print(f"[WORKER] Iniciado worker.")
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    
    while True:
        try:
            request = request_queue.get()
            if request is None:
                break

            operation = request[0]

            if operation == "upload":
                filename = request[1]
                content = request[2]
                result = handle_upload(filename, content)
                response_queue.put(result)
            
            elif operation == "download":
                filename = request[1]
                result = handle_download(filename)
                response_queue.put(result)
            
            elif operation == "delete":
                filename = request[1]
                result = handle_delete(filename)
                response_queue.put(result)

            elif operation == "list":
                print("[WORKER] Operacion: list", flush=True)
                result = handle_list_files()
                response_queue.put(result)

            else:
                response_queue.put(("error", "Comando desconocido"))

        except Exception as e:
            response_queue.put(("error", str(e)))

def handle_upload(filename, content):
    print(f"[WORKER] Subiendo archivo: {filename}, tamano: {len(content)}")
    file_path = os.path.join(STORAGE_DIR, filename)
    with open(file_path, 'wb') as f:
        f.write(content)
    return ("ok", f"Archivo '{filename}' subido correctamente.")

def handle_download(filename):
    print(f"[WORKER] Descargando archivo: {filename}")
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        return("error", "Archivo no encontrado")
    with open(file_path, 'rb') as f:
        data = f.read()
    return ("ok", data)

def handle_delete(filename):
    print(f"[WORKER] Borrando archivo: {filename}")
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        return ("error", "Archivo no encontrado")
    os.remove(file_path)
    return ("ok", f"Archivo '{filename}' eliminado.")

def handle_list_files():
    file_list = os.listdir(STORAGE_DIR)
    print(f"[WORKER] Listando archivos: {file_list}", flush=True)
    return ("ok", file_list)
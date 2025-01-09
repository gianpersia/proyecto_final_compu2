import socket
import sys
import socketserver
import subprocess
import argparse as ap
import os
import threading

#Directorio donde se guardaran los archivos
STORAGE_DIR = "/Users/gpersia/Documents/Facultad/proyecto_final_compu2/final/nube/Subidos"
download_path = f"../nube/Descargas"

def handle_client(client_socket): #gestion de la interaccion con un cliente
    try:
        print("Cliente conectado.") #log
        data = client_socket.recv(1024).decode()
        command = data.strip().split()
        operation = command[0]

        if operation == "upload":
            print("Operacion: upload") #log
            handle_upload(command, client_socket)
        elif operation == "download":
            handle_download(command, client_socket)
        elif operation == "list":
            handle_list(client_socket)
        else:
            client_socket.send(b"Error: comando inexistente\n")
    except Exception as e:
        print(f"Error en handle_client: {str(e)}") #log
        #client_socket.send(f"Error: {str(e)}\n".encode())
    finally:
        client_socket.close()
    
def handle_upload(command, client_socket): #gestion de subida de archivos
    buffer = b""
    try:
        print("[DEBUG] Esperando datos del cliente...")
        while True:
            data = client_socket.recv(1024)
            print(f"[DEBUG] Recibido fragmento crudo: {data}")
            if not data:
                print("[DEBUG] Conexion cerrada por el cliente.")
                break
            buffer += data

        #espera señal inicio por parte del cliente
        if b"\n" in buffer and b"START" in buffer.split(b"\n")[0]:
            start_signal, buffer = buffer.split(b"\n", 1)
            print(f"[DEBUG] Recibido START: {start_signal.decode().strip()}")

        #agrego longitud nombre archivo
        #filename_length = int(client_socket.recv(4).decode())
        #print(f"[DEBUG] Longitud del nombre del archivo: {filename_length}")
        
        #recibo nombre
        if b"\n" in buffer and b"START" in start_signal:
            filename, buffer = buffer.split(b"\n", 1) #separa nombre del resto
            filename = filename.decode().strip()
            print(f"[DEBUG] Recibido nombre archivo: {filename}") #log de datos crudos
            file_path = os.path.join(STORAGE_DIR, filename)
            print(f"[DEBUG] Guardando en: {file_path}") #log
        
        #recibo contenido y escribo
        with open(file_path, 'wb') as f:
            while True:
                if b"<END>" in buffer:
                    data, buffer = buffer.split(b"<END>", 1)
                    f.write(data)
                    print("[DEBUG] EOF recibido, finalizando escritura.")
                    break
                if buffer: 
                    f.write(buffer)
                    print(f"[DEBUG] Escrito al archivo: {len(buffer)} bytes") #log
                    buffer = b"" #limpio despues de escribir
                data = client_socket.recv(1024)
                if not data:
                    print("[DEBUG] Conexion cerrada por el cliente.")
                    return
                buffer += data
                
        client_socket.send(b"Archivo subido correctamente\n")
        print(f"[DEBUG] Archivo guardado correctamente.")
    except Exception as e:
        print(f"Error en handle_upload: {str(e)}")
    finally:
        client_socket.close() #cierro la conexion al terminar

def handle_download(command, client_socket): #gestion de descarga de archivos
    if len(command) < 2:
        client_socket.send(b"Falta nombre archivo\n")
        return

    filename = command[1]
    file_path = os.path.join(STORAGE_DIR, filename)

    if not os.path.exists(file_path):
        client_socket.send(b"Archivo no encontrado\n")
    else:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                client_socket.send(data)
        client_socket.send(b"EOF") #señal de fin de transmision

def handle_list(client_socket): #Archivos disponibles en la nube

    files = os.listdir(STORAGE_DIR)
    if not files:
        client_socket.send(b"No se encontraron archivos\n")
    else:
        client_socket.send("\n".join(files).encode() + b"\n")

def start_server(port): #inicio de servidor y conexiones entrantes
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"Running on port: {port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection established with {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Nube")
    parser.add_argument('-p', '--port', type=int, default=8080, help='Puerto servidor')
    args = parser.parse_args()

    start_server(args.port)
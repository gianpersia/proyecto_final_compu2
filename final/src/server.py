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
        client_socket.send(f"Error: {str(e)}\n".encode())

    client_socket.close()
    
def handle_upload(command, client_socket): #gestion de subida de archivos
    #recibo primer el nombre del archivo
    try:
        buffer = b"" #buffer interno para manejar datos fragmentados

        #espera señal inicio por parte del cliente
        while b"\n" not in buffer: # leo hasta salto de linea
            buffer += client_socket.recv(1024)
            start_signal, buffer = buffer.split(b"\n", 1) #separo senal del resto
        
        
        #start_signal = client_socket.recv(1024).decode().strip()
        print(f"[DEBUG] Recibido START: {start_signal.decode().strip()}") #log de datos crudos
        if start_signal.decode().strip() != "START":
            print("[DEBUG] Señal START no valida.")
            client_socket.send(b"Error: Senal de inicio no recibida\n")
            return
        
        #agrego longitud nombre archivo
        #filename_length = int(client_socket.recv(4).decode())
        #print(f"[DEBUG] Longitud del nombre del archivo: {filename_length}")
        
        #recibo nombre
        while b"\n" not in buffer:
            buffer += client_socket.recv(1024)
        filename, buffer = buffer.split(b"\n", 1) #separa nombre del resto
        filename = filename.decode().strip()
        #filename = client_socket.recv(1024).decode().strip()
        print(f"[DEBUG] Recibido nombre archivo: {filename}") #log de datos crudos
        #filename = filename.decode()

        if not filename or os.path.sep in filename:
            client_socket.send(b"Nombre de archivo no valido\n")
            return
    
        file_path = os.path.join(STORAGE_DIR, filename)
        print(f"[DEBUG] Guardando en: {file_path}") #log

    
        #recibo contenido y escribo
        with open(file_path, 'wb') as f:
            while True:
                if b"<END>" in buffer:
                    data, _ = buffer.split(b"<END>", 1)
                    f.write(data)
                #data = client_socket.recv(1024)
                #if data.endswith(b"<END>"): #senal fin archivo
                #    f.write(data[:-5]) #escribo sin el delimitador END
                #print(f"[DEBUG] Recibido dato valido: {data[:20]}") #log datos crudos
                #if data.strip() == b"EOF": #señal de fin de archivo, al reconocer esta señal, el servidor deja de escribir el archivo
                 #   print("[DEBUG] EOF recibido, finalizando escritura.")
                  #  break
                    print("[DEBUG] EOF recibido, finalizando escritura.")
                    break
                #f.write(data)
                f.write(buffer)
                buffer = client_socket.recv(1024) #leo mas datos

        client_socket.send(b"Archivo subido correctamente\n")
        print(f"[DEBUG] Archivo guardado correctamente.")
    except Exception as e:
        print(f"Error en handle_upload: {str(e)}")
        client_socket.send(f"Error al guardar archivo: {str(e)}\n".encode())
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
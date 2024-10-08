import socket
import sys
import socketserver
import subprocess
import argparse as ap
import os
import threading

#Directorio donde se guardaran los archivos
STORAGE_DIR = "/Users/gpersia/Documents/Facultad/proyecto_final_compu2/final" 

def handle_client(client_socket): #gestion de la interaccion con un cliente
    try:
        data = client_socket.recv(1024).decode()
        command = data.strip().split()
        operation = command[0]

        if operation == "upload":
            handle_upload(command, client_socket)
        elif operation == "download":
            handle_download(command, client_socket)
        elif operation == "list":
            handle_list(client_socket)
        else:
            client_socket.send(b"Error: comando inexistente\n")
    except Exception as e:
        client_socket.send(f"Error: {str(e)}\n".encode())

    client_socket.close()
    
def handle_upload(command, client_socket): #gestion de subida de archivos
    if len(command) < 2:
        client_socket.send(b"Falta nombre archivo\n")
        return
    
    filename = command[1]
    file_path = os.path.join(STORAGE_DIR, filename)

    with open(file_path, 'wb') as f:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            f.write(data)

    client_socket.send(b"Archivo subido\n")

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
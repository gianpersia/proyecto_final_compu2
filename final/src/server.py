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
        data = client_socket.recv(1024)
        if not data:
            client_socket.close()
            return
    
        lines = data.split(b"\n", 1)
        command_line = lines[0].decode().strip()
        
        leftover = b""
        if len(lines) > 1:
            leftover = lines[1]
    
        command_parts = command_line.split()
        operation = command_parts[0]

        if operation == "upload":
            print("Operacion: upload") #log
            handle_upload(client_socket, leftover)
        elif operation == "download":
            print("Operacion: download")
            handle_download(command_parts, client_socket)
        elif operation == "list":
            print("Operacion: listar")
            handle_list(client_socket)
        else:
            client_socket.sendall(b"Error: comando inexistente\n")
    except Exception as e:
        print(f"Error en handle_client: {e}")
    finally:
        client_socket.close()
    
def handle_upload(client_socket, buffer): #gestion de subida de archivos
    try:
    #file_path = None #inicializo file_path
    #try:
    #    print("[DEBUG] Esperando datos del cliente...")
        #while True:
        #    data = client_socket.recv(1024)
        #    print(f"[DEBUG] Recibido fragmento crudo: {data}")
        #    if not data: #si el cliente cierra la conexion, salir
        #        print("[DEBUG] Conexion cerrada por el cliente.")
        #        break
        #    buffer += data

        #espera señal inicio por parte del cliente
        #if b"\n" in buffer and b"START" in buffer.split(b"\n")[0]:
        while b"START\n" not in buffer:
            data = client_socket.recv(1024)
            if not data:
                raise ValueError("[DEBUG] Conexion cerrada antes de recibir la senal START")
            buffer += data
            print(f"[DEBUG] Buffer actual (bscando START): {buffer}")

        _, buffer = buffer.split(b"START\n", 1)
            #start_signal, buffer = buffer.split(b"\n", 1)
            #print(f"[DEBUG] Recibido START: {start_signal.decode().strip()}")
        
        #if b"START\n" in buffer:
            #buffer += client_socket.recv(1024)
            #_, buffer = buffer.split(b"START\n", 1)
        print("[DEBUG] Senal START recibida")
        #else:
        #    raise ValueError("[DEBUG] No se pudo procesar la senal START")
        #agrego longitud nombre archivo
        #filename_length = int(client_socket.recv(4).decode())
        #print(f"[DEBUG] Longitud del nombre del archivo: {filename_length}")
        
        #recibo nombre
        #if b"\n" in buffer and b"START" in start_signal:
        while b"\n" not in buffer:
            data = client_socket.recv(1024)
            if not data:
                raise ValueError("[DEBUG] Conexion cerrada antes de recibir el nombre del archivo")
            buffer += data
            print(f"[DEBUG] Buffer actual (buscando filename): {buffer}")
        
        #if b"\n" in buffer:
            #buffer += client_socket.recv(1024)
        filename, buffer = buffer.split(b"\n", 1) #separa nombre del resto
        filename = filename.decode().strip()
        #        print(f"[DEBUG] Recibido nombre archivo: {filename}") #log de datos crudos
        #else:
        #    raise ValueError("[DEBUG] No se pudo procesar el nombre del archivo")
        if not filename:
            raise ValueError("[DEBUG] Nombre de archivo vacio o no valido")
        
        print(f"[DEBUG] Recibido nombre archivo: {filename}")
        #    client_socket.send(b"Error: Nombre de archivo no valido\n")
        #    return
        
        file_path = os.path.join(STORAGE_DIR, filename)
        print(f"[DEBUG] Guardando en: {file_path}") #log

        #valido asignacion de file_path
        #if not file_path:
        #    print("[DEBUG] Error: No se puedo asignar el nombre del archivo.")
        #    client_socket.send(b"Error: No se recibio nombre del archivo\n")
        #    return
        
        #recibo contenido y escribo
        #    if b"<END>" in buffer:
        with open(file_path, 'wb') as f:
            while True:
                if b"<END>" in buffer:
                    content, buffer = buffer.split(b"<END>", 1)
                    f.write(content)
                    print("[DEBUG] EOF recibido, escritura completada.")
                    #if buffer: 
                    #    f.write(buffer)
                    #    print(f"[DEBUG] Escrito al archivo: {len(buffer)} bytes") #log
                    #    buffer = b"" #limpio despues de escribir
                    #data = client_socket.recv(1024)
                    #if not data:
                    #    print("[DEBUG] Conexion cerrada por el cliente.")
                    #    return
                    #buffer += data  
            
                #return
                    break
                f.write(buffer)
                buffer = client_socket.recv(1024)
                if not buffer:
                    raise ValueError("[DEBUG] Conexion cerrada antes de completar el archivo")

        client_socket.sendall(b"Archivo subido correctamente\n")
        print("[DEBUG] Archivo guardado correctamente.")
    except Exception as e:
        print(f"Error en handle_upload: {e}")
        client_socket.sendall(b"Error: No se pudo subir el archivo\n")
    finally:
      #  client_socket.close() #cierro la conexion al terminar
        print("[DEBUG] Conexion cerrada en handle_upload.")

def handle_download(command_parts, client_socket): #gestion de descarga de archivos
    print(f"[DEBUG] Comando de descarga: {command_parts}")
    if len(command_parts) < 2:
        client_socket.send(b"Falta nombre archivo\n")
        print("[DEBUG] Falta nombre archivo.")
        return

    filename = command_parts[1]
    file_path = os.path.join(STORAGE_DIR, filename)
    print(f"[DEBUG] Buscando archivo: {file_path}")

    if not os.path.exists(file_path):
        client_socket.send(b"Archivo no encontrado\n")
        print("[DEBUG] Archivo no encontrado.")
    else:
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                client_socket.send(data)
                print(f"[DEBUG] Enviando datos: {data[:20]}...")
        client_socket.send(b"EOF") #señal de fin de transmision
        print("[DEBUG] Senal EOF enviada.")

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
    #parser = ap.ArgumentParser(description="Nube")
    #parser.add_argument('-p', '--port', type=int, default=8080, help='Puerto servidor')
    #args = parser.parse_args()

    #start_server(args.port)

    PORT = 8080
    start_server(PORT)
import socket
import argparse as ap
import sys
import os

def send_command(server, port, command, filepath=None): #indicaciones para el servidor
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, port))

    client_socket.send(command.encode() + b"\n")
    print(f"[DEBUG] Enviado comando: {command}")

    if command.startswith("upload") and filepath: #subida de archivo
        #verificacion de que existe archivo
        if not os.path.exists(filepath):
            print(f"Error: El archivo '{filepath}' no existe.")
            client_socket.close()
            return
        
         #señal inicio
        client_socket.send(b"START\n")
        print("[DEBUG] Enviada señal START")
       
        #enviar nombre
        filename = os.path.basename(filepath)
        client_socket.send((filename + "\n").encode()) #archivo
        print(f"[DEBUG] Enviado nombre archivo: {filename}")

        #despues el contenido (esto lo hago porque siempre se estaba subiendo el archivo vacio)
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                client_socket.send(data)
                print(f"[DEBUG] Enviado datos: {data[:20]}...") #log

        client_socket.send(b"EOF\n") #señal fin de archivo con delimitador explicito
        print(f"[DEBUG] Enviada señal EOF.")

        #confirmacion del servidor porque si no me tira un error de excepcion broken pipe porque el cliente cierra la conexion antes de que el servidor termine

        response = client_socket.recv(1024)
        print(f"[DEBUG] Respuesta del servidor: {response.decode()}")

    elif command.startswith("download"): #descarga de archivo
        filename = command.split()[1]

        os.makedirs("../nube/Descargas", exist_ok=True) #se crea la carpeta si no existe
        download_path = f"../nube/Descargas/{filename}"

        with open(download_path, 'wb') as f:
            while True:
                data = client_socket.recv(1024)
                if data == b"EOF":
                    break
                f.write(data)
        print(f"Archivo descargado con exito: {download_path}")
    
    elif command.startswith("list"): #listado de archivos
        response = client_socket.recv(4096)
        print(f"Archivos disponibles:\n{response.decode()}")

    client_socket.close()
    print("[DEBUG] Conexion cerrada.")

if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Cliente nube")
    parser.add_argument("-s", '--server', type=str, required=True, help='Direccion del servidor')
    parser.add_argument("-p", '--port', type=int, default=8080, help='Puerto del servidor')
    parser.add_argument("-u", '--upload', type=str, help='Ruta del archivo a subir')
    parser.add_argument("-d", '--download', type=str, help='Nombre del archivo a descargar')
    parser.add_argument("-l", '--list', action='store_true', help='Listar archivos disponibles')

    args = parser.parse_args()

    if args.upload:
        command = f"upload {os.path.basename(args.upload)}"
        send_command(args.server, args.port, command, args.upload)
    elif args.download:
        command = f"download {args.download}"
        send_command(args.server, args.port, command)
    elif args.list:
        command = "list"
        send_command(args.server, args.port, command)
    else:
        print("Comando incorrecto, por favor introducir un comando valido: -u, -d, -l")
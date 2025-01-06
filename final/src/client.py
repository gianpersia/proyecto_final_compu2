import socket
import argparse as ap
import sys
import os

def send_command(server, port, command, filepath=None): #indicaciones para el servidor
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, port))

    client_socket.send(command.encode())

    if command.startswitch("upload") and filepath:
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                client_socket.send(data)

    response = client_socket.recv(4096)
    print(f"Respuesta: {response.decode()}")

    client_socket.close()

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
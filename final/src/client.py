import socket
import argparse as ap
import sys
import os
import time

def send_command(server, port, command, filepath=None): #indicaciones para el servidor
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, port))
    client_socket.settimeout(10) #incremento tiempo de espera a 10 segundos

    try:
        client_socket.sendall((command + "\n").encode())
        print(f"[DEBUG] Enviado comando: {command}")

        if command == "upload" and filepath: #subida de archivo
            #verificacion de que existe archivo
            if not os.path.exists(filepath):
                print(f"Error: El archivo '{filepath}' no existe.")
                #client_socket.close()
                return
        
            #señal inicio
            client_socket.sendall(b"START\n")
            print("[DEBUG] Enviada señal START")

        #enviar longitud
        #filename = os.path.basename(filepath)
        #filename_length = f"{len(filename):04}" #longitud como string de 4 caracteres
        #client_socket.send(filename_length.encode())
        #print(f"[DEBUG] Enviada longitud del nombre del archivo: {filename_length}")
       
            #enviar nombre
            filename = os.path.basename(filepath)
            client_socket.sendall((filename + "\n").encode()) #archivo
            print(f"[DEBUG] Enviado nombre archivo: {filename}")

            #despues el contenido (esto lo hago porque siempre se estaba subiendo el archivo vacio)
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client_socket.sendall(data)
                    print(f"[DEBUG] Enviando datos: {data[:20]}...") #log

            client_socket.sendall(b"<END>\n") #señal fin de archivo con delimitador unico
            print(f"[DEBUG] Enviada señal EOF.")

            #confirmacion del servidor porque si no me tira un error de excepcion broken pipe porque el cliente cierra la conexion antes de que el servidor termine
            try:   
                response = client_socket.recv(1024)
                print(f"[DEBUG] Respuesta del servidor: {response.decode()}")
            except socket.error as e:
                print(f"[DEBUG] Error al recibir respuesta del servidor: {str(e)}")
    
        elif command.startswith("download"): #descarga de archivo
            filename = command.split()[1]
            response = client_socket.recv(1024).decode()
            if response == "Archivo no encontrado\n":
                print("Error: El archivo solicitado no existe en el servidor.")
            else:
                os.makedirs("../nube/Descargas", exist_ok=True) #se crea la carpeta si no existe
                download_path = f"../nube/Descargas/{filename}"

                with open(download_path, 'wb') as f:
                    while True:
                        if response == "EOF":
                            break
                    #data = client_socket.recv(1024)
                    #if data == b"EOF":
                    #    break
                        f.write(response.encode())
                        print(f"[DEBUG] Recibiendo datos: {response[:20]}...")
                        response = client_socket.recv(1024).decode()
                print(f"Archivo descargado con exito: {download_path}")
    
        elif command.startswith("list"): #listado de archivos
            response = client_socket.recv(4096)
            print(f"Archivos disponibles:\n{response.decode()}")
        
    except Exception as e:
        print(f"[DEBUG] Error durante la operación: {str(e)}")

    finally:
        client_socket.close()
        print("[DEBUG] Conexión cerrada.")
    
if __name__ == "__main__":
    parser = ap.ArgumentParser(description="Cliente nube")
    parser.add_argument("-s", '--server', type=str, required=True, help='Direccion del servidor')
    parser.add_argument("-p", '--port', type=int, default=8080, help='Puerto del servidor')
    parser.add_argument("-u", '--upload', type=str, help='Ruta del archivo a subir')
    parser.add_argument("-d", '--download', type=str, help='Nombre del archivo a descargar')
    parser.add_argument("-l", '--list', action='store_true', help='Listar archivos disponibles')

    args = parser.parse_args()

    if args.upload:
        command = "upload"
        send_command(args.server, args.port, command, args.upload)
    elif args.download:
        command = f"download {args.download}"
        send_command(args.server, args.port, command)
    elif args.list:
        command = "list"
        send_command(args.server, args.port, command)
    else:
        print("Comando incorrecto, por favor introducir un comando valido: -u, -d, -l")
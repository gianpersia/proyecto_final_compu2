import socket
import argparse
import os

def send_command(server, port, command, filepath=None, username=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server, port))

    try:
        #envio la línea de comando, "upload\n" o "download file.txt\n"
        client_socket.sendall((command + "\n").encode())

        if command == "upload" and filepath:
            if not os.path.exists(filepath):
                print(f"Error: No existe el archivo local '{filepath}'")
                return

            #envio START\n
            client_socket.sendall(b"START\n")
            #envio filename\n
            filename = os.path.basename(filepath)
            client_socket.sendall((filename + "\n").encode())

            #envio usuario
            client_socket.sendall((username + "\n").encode())

            #envio contenido, y luego <END>
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(1024)
                    if not data:
                        break
                    client_socket.sendall(data)
            client_socket.sendall(b"<END>\n")  # delimitador

            #recibo respuesta
            response = client_socket.recv(4096).decode()
            print("Servidor dice:", response.strip())

        elif command.startswith("download"):
            #response = client_socket.recv(1024)
            #if response.startswith(b"Error:"):
            #    print(response.decode())
            #else:
            #espero recibir el contenido y luego la senal de finalizacion
            # 'command' podría ser "download file.txt"
                #content = response
            content = bytearray()
            while True:
                chunk = client_socket.recv(1024)
                if not chunk:
                        # Se cerró conexión
                    break
                    # Buscamos "EOF"
                eof_index = chunk.find(b"EOF")
                if eof_index != -1:
                    #if b"EOF" in chunk:
                        # Separar la parte previa a "EOF"
                        #before_eof = chunk.split(b"EOF", 1)[0]
                        #content += before_eof
                    content.extend(chunk[:eof_index])
                    break
                else:
                        #content += chunk
                    content.extend(chunk)

            if content.startswith(b"Error:"):
                print(content.decode())
            else:
            
            # reviso si se trata de un error
            # Podría ser "Error: Archivo no encontrado"
           
                DOWNLOAD_DIR = "/Users/gpersia/Documents/Facultad/proyecto_final_compu2/final/nube/Descargas"
                print("[DEBUG] Creando carpeta en:", DOWNLOAD_DIR)
                os.makedirs(DOWNLOAD_DIR, exist_ok=True)
                # Guardar el archivo
                filename = command.split()[1]
                download_path = os.path.join(DOWNLOAD_DIR, filename)
                with open(download_path, 'wb') as f:
                    f.write(content)
                print(f"Archivo descargado: {download_path}")

        elif command.startswith("delete"):
            #eperamos un mensaje de archivo eliminado o de error."
            response = client_socket.recv(1024).decode()
            print(response.strip())

        elif command.startswith("list"):
            # la lista de archivos o mensaje
            response = client_socket.recv(4096).decode()
            print(response.strip())

        else:
            print("Comando no reconocido (usa 'upload', 'download <file>', 'delete <file>', 'list').")

    except Exception as e:
        print("Error:", e)
    finally:
        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--server", required=True)
    parser.add_argument("-p", "--port", type=int, default=8080)
    parser.add_argument("-u", "--upload")
    parser.add_argument("-n", "--username", help="Nombre del usuario")
    parser.add_argument("-d", "--download")
    parser.add_argument("-r", "--remove")
    parser.add_argument("-l", "--list", action="store_true")
    args = parser.parse_args()

    if args.upload:
        if not args.username:
            print("Error: El argumento --username es obligatorio para 'upload'.")
        else:
            send_command(args.server, args.port, "upload", args.upload, args.username)
    elif args.download:
        command = f"download {args.download}"
        send_command(args.server, args.port, command)
    elif args.remove:
        command = f"delete {args.remove}"
        send_command(args.server, args.port, command)
    elif args.list:
        command = "list"
        send_command(args.server, args.port, command)
    else:
        print("Usa -u <file>, -d <file>, -r <file> o -l para listar")

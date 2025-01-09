import socket

def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)
    print(f"Running on port: {port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection established with {addr}")

        buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                print("[DEBUG] Conexión cerrada por el cliente.")
                break
            print(f"[DEBUG] Recibido fragmento crudo: {data}")
            buffer += data

        print("[DEBUG] Buffer completo recibido:")
        print(buffer)
        client_socket.close()

if __name__ == "__main__":
    start_server(8080)

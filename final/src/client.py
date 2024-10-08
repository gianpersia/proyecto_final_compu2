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
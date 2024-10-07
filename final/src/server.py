import socket
import sys
import socketserver
import subprocess
import argarpse as ap
import os
import threading

#Directorio donde se guardaran los archivos
STORAGE_DIR = "/Users/gpersia/Documents/Facultad/proyecto_final_compu2/final" 

class MyTCPHandler(socketserver.BaseRequestHandler):

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
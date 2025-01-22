import subprocess

commands = [
    ["python", "async_client.py", "-s", "127.0.0.1", "-p", "8080", "-u", "/Users/gpersia/Downloads/prueba.txt", "-n", "TestA"],
    ["python", "async_client.py", "-s", "127.0.0.1", "-p", "8080", "-u", "/Users/gpersia/Downloads/prueba1.txt", "-n", "TestB"],
    ["python", "async_client.py", "-s", "127.0.0.1", "-p", "8080", "-l"],
    ["python", "async_client.py", "-s", "127.0.0.1", "-p", "8080", "-d", "prueba.txt"]
]

processes = []
for cmd in commands:
    p = subprocess.Popen(cmd)
    processes.append(p)

for p in processes:
    p.wait()

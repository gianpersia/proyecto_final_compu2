from celery import Celery
import os

celery_app = Celery("nube_app", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

STORAGE_DIR = "/Users/gpersia/Documents/Facultad/proyecto_final_compu2/final/nube/Subidos"

@celery_app.task
def upload_file(filename, content_bytes):
    #subir archivos
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    file_path = os.path.join(STORAGE_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content_bytes)
    return f"Archivo '{filename}' subido correctamente."

@celery_app.task
def download_file(filename):
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        return None
    with open(file_path, "rb") as f:
        data = f.read()
    return data

@celery_app.task
def delete_file(filename):
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        return f"Error: Archivo '{filename}' no existe."
    os.remove(file_path)
    return f"Archivo '{filename}' eliminado."

@celery_app.task
def list_files():
    if not os.path.exists(STORAGE_DIR):
        return []
    return os.listdir(STORAGE_DIR)
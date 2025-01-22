from celery import Celery
import os
from db import init_db, DB_PATH
import sqlite3

init_db()

celery_app = Celery("nube_app", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

STORAGE_DIR = "/Users/gpersia/Documents/Facultad/proyecto_final_compu2/final/nube/Subidos"

@celery_app.task
def upload_file(filename, content_bytes, username):
    #subir archivos
    if not os.path.exists(STORAGE_DIR):
        os.makedirs(STORAGE_DIR)
    
    file_path = os.path.join(STORAGE_DIR, filename)
    if os.path.exists(file_path):
        return f"Error: El archivo '{filename}' ya existe en el disco."
    
    with open(file_path, "wb") as f:
        f.write(content_bytes)
    
    size = len(content_bytes)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        try:
            c.execute("""
                INSERT INTO FILES (filename, size, username)
                VALUES (?, ?, ?)
            """, (filename, size, username))
            conn.commit()
        except sqlite3.IntegrityError:
            return f"Error: El archivo '{filename} ya esta registrado en la DB."
        
    return f"Archivo '{filename}' subido correctamente por '{username}' (size={size} bytes)."

@celery_app.task
def download_file(filename):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("SELECT filename FROM files WHERE filename = ?", (filename,))
            row = c.fetchone()

        if not row:
            return f"Error: El archivo '{filename}' no esta registrado en la DB."
    
        file_path = os.path.join(STORAGE_DIR, filename)
        if not os.path.exists(file_path):
            return f"Error: El archivo '{filename}' no existe en el disco."
    
        with open(file_path, "rb") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error al descargar el archivo; {e}"

@celery_app.task
def delete_file(filename):
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        return f"Error: Archivo '{filename}' no existe."
    os.remove(file_path)
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            DELETE FROM files
            WHERE filename = ?
        """, (filename,))
        conn.commit()

    return f"Archivo '{filename}' eliminado."

@celery_app.task
def list_files():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT filename, username FROM files")
        rows = c.fetchall()

        if not rows:
            return "No se encontraron archivos."
        
        lines = []
        for row in rows:
            fname, uname = row
            lines.append(f"{fname} (subido por: {uname})")
        return "\n".join(lines)
        
        #return "\n".join([f"{row[0]} (subido por: {row[1]})" for row in rows])
    
    filenames = [row[0] for row in rows]
    return filenames

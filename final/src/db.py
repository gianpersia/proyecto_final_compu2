import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "metadata.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS files ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "filename TEXT UNIQUE NOT NULL, "
                "size INTEGER NOT NULL, "
                "upload_data DATETIME DEFAULT CURRENT_TIMESTAMP, "
                "username TEXT)"
        )
        conn.commit()
    add_user_column()

def add_user_column():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("PRAGMA table_info(files);")
        columns = [row[1] for row in c.fetchall()]
        if "username" not in columns:
            c.execute("ALTER TABLE files ADD COLUMN username TEXT;")
            conn.commit()
            print("[DEBUG] Columna 'username' agregada a la tabla 'files'.")
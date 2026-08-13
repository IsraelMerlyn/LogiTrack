import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_PATH = "users.db"

def init_and_seed():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            ultimo_login TEXT NOT NULL
        )
    """)

    cursor.execute("CREATE INDEX idx_users_id ON users(id);")

    nombres = ["Carlos", "Ana", "Luis", "Maria", "Jorge", "Sofia", "Diego", "Elena", "Fernando", "Lucia"]
    apellidos = ["Lopez", "Garcia", "Perez", "Rodriguez", "Martinez", "Hernandez", "Gomez", "Diaz"]
    dominios = ["logitrack.com", "gmail.com", "outlook.com", "empresa.net"]

    base_date = datetime.now()
    batch = []

    for i in range(1, 10001):
        nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
        email = f"usuario_{i}@{random.choice(dominios)}"
        ultimo_login = (base_date - timedelta(minutes=random.randint(1, 50000))).isoformat()
        batch.append((nombre, email, ultimo_login))

    cursor.executemany("INSERT INTO users (nombre, email, ultimo_login) VALUES (?, ?, ?)", batch)
    conn.commit()
    conn.close()
    print(f"✅ Base de datos 'users.db' generada exitosamente con 10,000 registros.")

if __name__ == "__main__":
    init_and_seed()

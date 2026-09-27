import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица пользователей и настроек
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        hr_max INTEGER DEFAULT 180,
        gender TEXT DEFAULT 'man'
    )
    """)
    
    # Таблица обуви пользователя
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_shoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        brand TEXT,
        model TEXT,
        size_us REAL,
        size_eur REAL,
        size_cm REAL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    """)
    
    conn.commit()
    conn.close()

def get_user_settings(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT hr_max, gender FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"hr_max": row[0], "gender": row[1]}
    return {"hr_max": 180, "gender": "man"}

def update_user_hr_max(user_id: int, hr_max: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (user_id, hr_max) VALUES (?, ?)
    ON CONFLICT(user_id) DO UPDATE SET hr_max = excluded.hr_max
    """, (user_id, hr_max))
    conn.commit()
    conn.close()

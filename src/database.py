import sqlite3
import os

# Path to our database file
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'honeypot.db')

def init_db():
    """Creates the database and table if they don't exist yet."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip        TEXT NOT NULL,
            username  TEXT NOT NULL,
            password  TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("[DB] Database ready.")

def log_attempt(ip, username, password):
    """Logs a single login attempt to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO attempts (ip, username, password)
        VALUES (?, ?, ?)
    ''', (ip, username, password))

    conn.commit()
    conn.close()
    print(f"[LOG] {ip} tried -> {username}:{password}")

def get_all_attempts():
    """Returns all logged attempts for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT timestamp, ip, username, password
        FROM attempts
        ORDER BY timestamp DESC
    ''')

    rows = cursor.fetchall()
    conn.close()
    return rows
if __name__ == "__main__":
    init_db()
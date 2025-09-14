
import sqlite3, time, os


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS traffic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            download_mbps REAL,
            upload_mbps REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(download, upload):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO traffic (timestamp, download_mbps, upload_mbps) VALUES (?, ?, ?)",
              (time.strftime("%Y-%m-%d %H:%M:%S"), download, upload))
    conn.commit()
    conn.close()

def get_history(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, download_mbps, upload_mbps FROM traffic ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows
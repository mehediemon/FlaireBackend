import sqlite3

DB_PATH = "user.db"  # Path to your SQLite database file

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the `tasks` table if it doesn't already exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            username TEXT,
            password TEXT)
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
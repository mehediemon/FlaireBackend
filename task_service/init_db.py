import sqlite3

DB_PATH = "tasks.db"  # Path to your SQLite database file

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create the `tasks` table if it doesn't already exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        completed BOOLEAN NOT NULL DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
import sqlite3

def init_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

   
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')


    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            standard INTEGER NOT NULL,
            science_score INTEGER NOT NULL,
            maths_score INTEGER NOT NULL,
            reasoning_score INTEGER NOT NULL,
            total_score INTEGER NOT NULL,
            counseling_stream TEXT NOT NULL,
            counseling_reason TEXT NOT NULL,
            test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
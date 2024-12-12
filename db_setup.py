import sqlite3

def setup_database():
    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT UNIQUE NOT NULL,
        ssn TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Additional Emails table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        email TEXT NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Additional Phones table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_phones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        phone TEXT NOT NULL UNIQUE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Bank Accounts table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bank_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        account_number TEXT NOT NULL UNIQUE,
        routing_number TEXT NOT NULL,
        phone TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        transaction_type TEXT NOT NULL,
        FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Best Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS best_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_sent REAL DEFAULT 0,
        total_received REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Transactions Summary table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions_summary (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        month TEXT NOT NULL,
        total_sent REAL DEFAULT 0,
        total_received REAL DEFAULT 0,
        average_sent REAL DEFAULT 0,
        average_received REAL DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    ''')

    # Populate Best Users table
    cursor.execute('''
    INSERT OR IGNORE INTO best_users (user_id, total_sent, total_received)
    SELECT id, 0, 0 FROM users
    ''')

    # Create indices for efficient querying
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender ON transactions (sender_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_receiver ON transactions (receiver_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON transactions (date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_month ON transactions_summary (month)')

    # Populate Transactions Summary table
    cursor.execute('''
    INSERT OR IGNORE INTO transactions_summary (user_id, month, total_sent, total_received, average_sent, average_received)
    SELECT
        sender_id AS user_id,
        strftime('%Y-%m', date) AS month,
        SUM(CASE WHEN transaction_type = 'send' THEN amount ELSE 0 END) AS total_sent,
        SUM(CASE WHEN transaction_type = 'receive' THEN amount ELSE 0 END) AS total_received,
        AVG(CASE WHEN transaction_type = 'send' THEN amount ELSE NULL END) AS average_sent,
        AVG(CASE WHEN transaction_type = 'receive' THEN amount ELSE NULL END) AS average_received
    FROM transactions
    GROUP BY user_id, month
    ''')

    conn.commit()
    conn.close()
    print("Database setup completed.")

if __name__ == "__main__":
    setup_database()

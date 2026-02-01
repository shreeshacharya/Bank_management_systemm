# bank_database.py (SQLite replacement for bank_backend.py)

import sqlite3

DB_NAME = 'accounts.db'

# Initialize the database with an accounts table
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            accNo INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT NOT NULL CHECK (type IN ('S', 'C')),
            deposit INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Create a new account
def create_account(accNo, name, acc_type, deposit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO accounts (accNo, name, type, deposit) VALUES (?, ?, ?, ?)',
              (accNo, name, acc_type, deposit))
    conn.commit()
    conn.close()

# Get all accounts
def get_all_accounts():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM accounts')
    accounts = c.fetchall()
    conn.close()
    return accounts

# Get account balance by accNo
def get_balance(accNo):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT deposit FROM accounts WHERE accNo = ?', (accNo,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_account(accNo):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT accNo, name, type, deposit FROM accounts WHERE accNo = ?', (accNo,))
    row = c.fetchone()
    conn.close()
    return row

# Deposit or Withdraw (mode=1: deposit, mode=2: withdraw)
def update_balance(accNo, amount, mode):
    current = get_balance(accNo)
    if current is None:
        raise ValueError("Account not found")
    if mode == 2 and amount > current:
        raise ValueError("Insufficient balance")
    new_balance = current + amount if mode == 1 else current - amount

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('UPDATE accounts SET deposit = ? WHERE accNo = ?', (new_balance, accNo))
    conn.commit()
    conn.close()

# Delete account
def delete_account(accNo):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('DELETE FROM accounts WHERE accNo = ?', (accNo,))
    conn.commit()
    conn.close()

# Modify account details
def modify_account(accNo, name, acc_type, deposit):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        UPDATE accounts SET name = ?, type = ?, deposit = ? WHERE accNo = ?
    ''', (name, acc_type, deposit, accNo))
    conn.commit()
    conn.close()

# For dashboard: get summary counts
def get_dashboard_stats():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT COUNT(*), SUM(deposit) FROM accounts')
    total_accounts, total_balance = c.fetchone()
    c.execute("SELECT COUNT(*) FROM accounts WHERE type = 'S'")
    saving_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM accounts WHERE type = 'C'")
    current_count = c.fetchone()[0]
    conn.close()
    return total_accounts or 0, total_balance or 0, saving_count or 0, current_count or 0

# Initialize the DB when this file is imported
init_db()
# Users table for login/signup
def init_users_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def validate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    result = c.fetchone()
    conn.close()
    return result is not None

# Call this when file is loaded
init_users_table()

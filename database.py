import sqlite3

conn = sqlite3.connect("banking.db")
cursor = conn.cursor()

# ---------------- USERS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    account_no TEXT PRIMARY KEY,
    account_holder_name TEXT,
    username TEXT UNIQUE,
    password TEXT,
    opening_balance REAL,
    balance REAL,
    mobile TEXT,
    address TEXT,
    pan TEXT,
    aadhaar TEXT,
    account_type TEXT
)
""")

# ---------------- TRANSACTIONS TABLE ---------------- #

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_no TEXT,
    transaction_type TEXT,
    amount REAL,
    date_time TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")
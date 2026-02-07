import sqlite3
from faker import Faker
import random
from werkzeug.security import generate_password_hash

fake = Faker()
DB_NAME = "company_data.sqlite"

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create tables (same as before)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            total_spent REAL,
            last_order_date TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password_hash TEXT,
            ssn TEXT,
            salary INTEGER,
            department TEXT
        )
    ''')

    # Clear old data if it exists so we don't duplicate
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM users")

    # Add mock data for Customers
    for _ in range(50):
        cursor.execute('''
            INSERT INTO customers (name, email, total_spent, last_order_date)
            VALUES (?, ?, ?, ?)
        ''', (fake.name(), fake.email(), round(random.uniform(10, 5000), 2), str(fake.date_this_year())))

    # Add mock data for Sensitive Users with real hashes
    departments = ['Engineering', 'Sales', 'HR', 'Legal']
    for _ in range(10):
        # Generate a real hash for a random "fake" password
        real_looking_hash = generate_password_hash(fake.password())
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, ssn, salary, department)
            VALUES (?, ?, ?, ?, ?)
        ''', (fake.user_name(), real_looking_hash, fake.ssn(), random.randint(50000, 150000), random.choice(departments)))

    conn.commit()
    conn.close()
    print(f"Mock Data {DB_NAME} Generated")

if __name__ == "__main__":
    setup_database()
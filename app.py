from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import date, timedelta, datetime
from functools import wraps
import re
import traceback
import os  # <-- ADD THIS for environment variables

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# ---------------------------
# DATABASE CONNECTION - UPDATED FOR PRODUCTION
# ---------------------------
def get_db_connection():
    # Use environment variables on Render
    if os.environ.get('RENDER'):  # Running on Render
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME')
        )
    else:  # Running locally
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="sale"
        )
    return conn

# ---------------------------
# INITIALIZE DATABASE TABLES
# ---------------------------
def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                quantity INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                join_date DATE DEFAULT (CURDATE()),
                status ENUM('active', 'inactive') DEFAULT 'active'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrow_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT NOT NULL,
                member_id INT NOT NULL,
                borrow_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                status ENUM('borrowed', 'returned', 'overdue') DEFAULT 'borrowed',
                FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                role ENUM('admin', 'librarian') DEFAULT 'librarian'
            )
        """)
        
        # Insert default admin
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, email, role) VALUES ('admin', 'admin123', 'admin@library.com', 'admin')")
        
        # Insert sample data
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO books (title, author, quantity) VALUES (%s, %s, %s)",
                [
                    ("The Great Gatsby", "F. Scott Fitzgerald", 5),
                    ("To Kill a Mockingbird", "Harper Lee", 3),
                    ("1984", "George Orwell", 4),
                    ("Pride and Prejudice", "Jane Austen", 2),
                    ("The Catcher in the Rye", "J.D. Salinger", 1)
                ]
            )
        
        cursor.execute("SELECT COUNT(*) FROM members")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO members (name, email, phone, status) VALUES (%s, %s, %s, 'active')",
                [
                    ("John Doe", "john@example.com", "1234567890"),
                    ("Jane Smith", "jane@example.com", "0987654321"),
                    ("Bob Johnson", "bob@example.com", "5555555555")
                ]
            )
        
        conn.commit()
        print("✅ Database ready!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

# ---------------------------
# LOGIN DECORATOR
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

# ---------------------------
# ROUTES (Your existing routes go here)
# ---------------------------
# ... (ALL your existing route functions - dashboard, books, borrow_book, etc.)
# ... (Copy everything from your previous app.py here)

# ---------------------------
# RUN APP - UPDATED FOR RENDER
# ---------------------------
if __name__ == '__main__':
    # Initialize database (skip on Render since we'll use external DB)
    if not os.environ.get('RENDER'):
        init_database()
    
  if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
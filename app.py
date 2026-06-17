from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date, timedelta, datetime
from functools import wraps
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db_connection():
    if os.environ.get('RENDER'):
        conn = psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME', 'library'),
            port=os.environ.get('DB_PORT', 5432)
        )
        return conn
    else:
        # Local development fallback
        import sqlite3
        conn = sqlite3.connect('library.db')
        conn.row_factory = sqlite3.Row
        return conn

# ---------------------------
# LOGIN DECORATOR
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# INITIALIZE DATABASE TABLES
# ---------------------------
def init_database():
    """Create all tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                role VARCHAR(20) DEFAULT 'librarian'
            )
        """)
        
        # Create books table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                quantity INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone VARCHAR(20),
                join_date DATE DEFAULT CURRENT_DATE,
                status VARCHAR(20) DEFAULT 'active'
            )
        """)
        
        # Create borrow_records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS borrow_records (
                id SERIAL PRIMARY KEY,
                book_id INT NOT NULL REFERENCES books(id) ON DELETE CASCADE,
                member_id INT NOT NULL REFERENCES members(id) ON DELETE CASCADE,
                borrow_date DATE NOT NULL,
                due_date DATE NOT NULL,
                return_date DATE,
                status VARCHAR(20) DEFAULT 'borrowed'
            )
        """)
        
        # Insert default admin if not exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                ('admin', 'admin123', 'admin@library.com', 'admin')
            )
            print("✅ Admin user created!")
        
        # Insert sample books if empty
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            books = [
                ("The Great Gatsby", "F. Scott Fitzgerald", 5),
                ("To Kill a Mockingbird", "Harper Lee", 3),
                ("1984", "George Orwell", 4),
                ("Pride and Prejudice", "Jane Austen", 2),
                ("The Catcher in the Rye", "J.D. Salinger", 1)
            ]
            cursor.executemany(
                "INSERT INTO books (title, author, quantity) VALUES (%s, %s, %s)",
                books
            )
            print("✅ Sample books added!")
        
        # Insert sample members if empty
        cursor.execute("SELECT COUNT(*) FROM members")
        if cursor.fetchone()[0] == 0:
            members = [
                ("John Doe", "john@example.com", "1234567890"),
                ("Jane Smith", "jane@example.com", "0987654321"),
                ("Bob Johnson", "bob@example.com", "5555555555")
            ]
            cursor.executemany(
                "INSERT INTO members (name, email, phone, status) VALUES (%s, %s, %s, 'active')",
                members
            )
            print("✅ Sample members added!")
        
        conn.commit()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Database error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# Call init_database when the app starts
init_database()

# ---------------------------
# ROUTES
# ---------------------------

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT COUNT(*) as total FROM books")
    total_books = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM books WHERE quantity > 0")
    available = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM borrow_records WHERE status = 'borrowed'")
    borrowed = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM borrow_records WHERE status = 'overdue'")
    overdue = cursor.fetchone()['total']
    
    cursor.execute("SELECT * FROM books WHERE quantity <= 2")
    low_stock = cursor.fetchall()
    
    cursor.execute("""
        SELECT b.title, m.name, br.borrow_date, br.due_date 
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        JOIN members m ON br.member_id = m.id
        WHERE br.status = 'borrowed'
        ORDER BY br.borrow_date DESC LIMIT 5
    """)
    recent = cursor.fetchall()
    
    conn.close()
    return render_template('dashboard.html', 
                         total_books=total_books, 
                         available=available, 
                         borrowed=borrowed,
                         overdue=overdue,
                         low_stock=low_stock,
                         recent=recent)

@app.route('/books')
@login_required
def books():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM books ORDER BY title")
    books = cursor.fetchall()
    conn.close()
    return render_template('books.html', books=books)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        quantity = int(request.form['quantity'])
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title, author, quantity) VALUES (%s, %s, %s)", (title, author, quantity))
        conn.commit()
        conn.close()
        flash(f'✅ "{title}" added successfully!', 'success')
        return redirect(url_for('books'))
    return render_template('add_book.html')

@app.route('/edit_book/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        quantity = int(request.form['quantity'])
        cursor.execute("UPDATE books SET title=%s, author=%s, quantity=%s WHERE id=%s", (title, author, quantity, id))
        conn.commit()
        conn.close()
        flash('✅ Book updated!', 'success')
        return redirect(url_for('books'))
    cursor.execute("SELECT * FROM books WHERE id=%s", (id,))
    book = cursor.fetchone()
    conn.close()
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('🗑️ Book deleted!', 'info')
    return redirect(url_for('books'))

@app.route('/borrow_book', methods=['GET', 'POST'])
@login_required
def borrow_book():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        book_id = request.form['book_id']
        member_id = request.form['member_id']
        due_date = request.form.get('due_date')
        
        cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
        book = cursor.fetchone()
        if not book or book['quantity'] <= 0:
            flash('❌ Book not available!', 'error')
            return redirect(url_for('borrow_book'))
        
        cursor.execute("SELECT * FROM members WHERE id=%s AND status='active'", (member_id,))
        member = cursor.fetchone()
        if not member:
            flash('❌ Member not found or inactive!', 'error')
            return redirect(url_for('borrow_book'))
        
        cursor.execute("SELECT * FROM borrow_records WHERE book_id=%s AND member_id=%s AND status='borrowed'", (book_id, member_id))
        if cursor.fetchone():
            flash('⚠️ This member already borrowed this book!', 'warning')
            return redirect(url_for('borrow_book'))
        
        borrow_date = date.today()
        if due_date:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
        else:
            due_date = borrow_date + timedelta(days=14)
        
        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE id=%s", (book_id,))
        cursor.execute("INSERT INTO borrow_records (book_id, member_id, borrow_date, due_date, status) VALUES (%s, %s, %s, %s, 'borrowed')", 
                      (book_id, member_id, borrow_date, due_date))
        conn.commit()
        conn.close()
        
        flash(f'✅ "{book["title"]}" borrowed by {member["name"]}!', 'success')
        return redirect(url_for('borrowed'))
    
    cursor.execute("SELECT * FROM books WHERE quantity > 0 ORDER BY title")
    books = cursor.fetchall()
    cursor.execute("SELECT * FROM members WHERE status='active' ORDER BY name")
    members = cursor.fetchall()
    conn.close()
    
    return render_template('borrow_book.html', 
                         books=books, 
                         members=members,
                         today=date.today(),
                         default_due=date.today() + timedelta(days=14))

@app.route('/borrowed')
@login_required
def borrowed():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("UPDATE borrow_records SET status='overdue' WHERE status='borrowed' AND due_date < CURRENT_DATE")
    conn.commit()
    
    cursor.execute("""
        SELECT br.*, b.title as book_title, m.name as member_name,
        EXTRACT(DAY FROM (CURRENT_DATE - br.due_date)) as days_overdue
        FROM borrow_records br
        JOIN books b ON br.book_id = b.id
        JOIN members m ON br.member_id = m.id
        ORDER BY br.borrow_date DESC
    """)
    records = cursor.fetchall()
    conn.close()
    
    return render_template('borrowed.html', records=records)

@app.route('/return_book/<int:id>', methods=['POST'])
@login_required
def return_book(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM borrow_records WHERE id=%s", (id,))
    record = cursor.fetchone()
    if record and record['status'] != 'returned':
        cursor.execute("UPDATE borrow_records SET return_date=CURRENT_DATE, status='returned' WHERE id=%s", (id,))
        cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE id=%s", (record['book_id'],))
        conn.commit()
        flash('✅ Book returned!', 'success')
    conn.close()
    return redirect(url_for('borrowed'))

@app.route('/members')
@login_required
def members():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM members ORDER BY name")
    members = cursor.fetchall()
    conn.close()
    return render_template('members.html', members=members)

@app.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO members (name, email, phone) VALUES (%s, %s, %s)", (name, email, phone))
            conn.commit()
            flash(f'✅ Member "{name}" added!', 'success')
        except Exception as e:
            flash('❌ Email already exists!', 'error')
        conn.close()
        return redirect(url_for('members'))
    return render_template('add_member.html')

@app.route('/edit_member/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        status = request.form['status']
        try:
            cursor.execute("UPDATE members SET name=%s, email=%s, phone=%s, status=%s WHERE id=%s", 
                          (name, email, phone, status, id))
            conn.commit()
            flash('✅ Member updated!', 'success')
        except:
            flash('❌ Email already exists!', 'error')
        conn.close()
        return redirect(url_for('members'))
    cursor.execute("SELECT * FROM members WHERE id=%s", (id,))
    member = cursor.fetchone()
    conn.close()
    return render_template('edit_member.html', member=member)

@app.route('/delete_member/<int:id>', methods=['POST'])
@login_required
def delete_member(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    flash('🗑️ Member deleted!', 'info')
    return redirect(url_for('members'))

# ---------------------------
# RUN APP
# ---------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
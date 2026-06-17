from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import date, timedelta, datetime
from functools import wraps
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_db_connection():
    # Always use PostgreSQL on Render
    print("📊 Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host='dpg-d8p62cj6sc1c73cdt590-a.virginia-postgres.render.com',
        user='libraryuser',
        password='AaCrgEda9PjShZEWZq6dAJl6Un0m28ZB',
        database='library_yiqs',
        port=5432
    )
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
        print("📊 Creating tables...")
        
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

# Initialize database when app starts
print("🚀 Initializing database...")
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
        print(f"🔐 Login attempt: {username}")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome back, {username}!', 'success')
                print(f"✅ Login successful: {username}")
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials!', 'error')
                print(f"❌ Login failed: {username}")
        except Exception as e:
            print(f"❌ Login error: {e}")
            flash('An error occurred. Please try again.', 'error')
    
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
    
    try:
        cursor.execute("SELECT COUNT(*) as total FROM books")
        total_books = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM books WHERE quantity > 0")
        available = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM borrow_records WHERE status = 'borrowed'")
        borrowed = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM borrow_records WHERE status = 'overdue'")
        overdue = cursor.fetchone()['total']
        
        cursor.execute("SELECT * FROM books WHERE quantity <= 2 ORDER BY quantity")
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
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        total_books = 0
        available = 0
        borrowed = 0
        overdue = 0
        low_stock = []
        recent = []
    finally:
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
    try:
        cursor.execute("SELECT * FROM books ORDER BY title")
        books = cursor.fetchall()
    except Exception as e:
        print(f"❌ Books error: {e}")
        books = []
    finally:
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
        try:
            cursor.execute("INSERT INTO books (title, author, quantity) VALUES (%s, %s, %s)", (title, author, quantity))
            conn.commit()
            flash(f'✅ "{title}" added successfully!', 'success')
        except Exception as e:
            print(f"❌ Add book error: {e}")
            flash('Error adding book!', 'error')
        finally:
            conn.close()
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
        try:
            cursor.execute("UPDATE books SET title=%s, author=%s, quantity=%s WHERE id=%s", (title, author, quantity, id))
            conn.commit()
            flash('✅ Book updated!', 'success')
        except Exception as e:
            print(f"❌ Edit book error: {e}")
            flash('Error updating book!', 'error')
        finally:
            conn.close()
        return redirect(url_for('books'))
    
    try:
        cursor.execute("SELECT * FROM books WHERE id=%s", (id,))
        book = cursor.fetchone()
    except Exception as e:
        print(f"❌ Get book error: {e}")
        book = None
    finally:
        conn.close()
    
    if not book:
        flash('Book not found!', 'error')
        return redirect(url_for('books'))
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:id>', methods=['POST'])
@login_required
def delete_book(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM books WHERE id=%s", (id,))
        conn.commit()
        flash('🗑️ Book deleted!', 'info')
    except Exception as e:
        print(f"❌ Delete book error: {e}")
        flash('Error deleting book!', 'error')
    finally:
        conn.close()
    return redirect(url_for('books'))

# ---------------------------
# BORROW BOOK FUNCTIONALITY
# ---------------------------
@app.route('/borrow_book', methods=['GET', 'POST'])
@login_required
def borrow_book():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    if request.method == 'POST':
        try:
            book_id = request.form['book_id']
            member_id = request.form['member_id']
            due_date = request.form.get('due_date')
            
            # Check if book exists and is available
            cursor.execute("SELECT * FROM books WHERE id=%s", (book_id,))
            book = cursor.fetchone()
            if not book:
                flash('❌ Book not found!', 'error')
                return redirect(url_for('borrow_book'))
            
            if book['quantity'] <= 0:
                flash(f'❌ Book "{book["title"]}" is not available!', 'error')
                return redirect(url_for('borrow_book'))
            
            # Check if member exists
            cursor.execute("SELECT * FROM members WHERE id=%s AND status='active'", (member_id,))
            member = cursor.fetchone()
            if not member:
                flash('❌ Member not found or inactive!', 'error')
                return redirect(url_for('borrow_book'))
            
            # Check if already borrowed
            cursor.execute("""
                SELECT * FROM borrow_records 
                WHERE book_id=%s AND member_id=%s AND status='borrowed'
            """, (book_id, member_id))
            existing = cursor.fetchone()
            if existing:
                flash(f'⚠️ {member["name"]} already borrowed this book!', 'warning')
                return redirect(url_for('borrow_book'))
            
            # Process borrow
            borrow_date = date.today()
            if due_date:
                due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            else:
                due_date = borrow_date + timedelta(days=14)
            
            # Update book quantity
            cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE id=%s", (book_id,))
            
            # Create borrow record
            cursor.execute("""
                INSERT INTO borrow_records (book_id, member_id, borrow_date, due_date, status)
                VALUES (%s, %s, %s, %s, 'borrowed')
            """, (book_id, member_id, borrow_date, due_date))
            
            conn.commit()
            flash(f'✅ "{book["title"]}" borrowed by {member["name"]}!', 'success')
            
        except Exception as e:
            print(f"❌ Borrow error: {e}")
            flash('Error borrowing book!', 'error')
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('borrowed'))
    
    # GET request - show form
    try:
        cursor.execute("SELECT * FROM books WHERE quantity > 0 ORDER BY title")
        books = cursor.fetchall()
        
        cursor.execute("SELECT * FROM members WHERE status='active' ORDER BY name")
        members = cursor.fetchall()
        
        cursor.execute("""
            SELECT br.*, b.title as book_title, m.name as member_name
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            JOIN members m ON br.member_id = m.id
            WHERE br.status IN ('borrowed', 'overdue')
            ORDER BY br.borrow_date DESC
            LIMIT 10
        """)
        current_borrows = cursor.fetchall()
        
    except Exception as e:
        print(f"❌ Borrow form error: {e}")
        books = []
        members = []
        current_borrows = []
    finally:
        conn.close()
    
    return render_template('borrow_book.html',
                         books=books,
                         members=members,
                         current_borrows=current_borrows,
                         today=date.today(),
                         default_due=date.today() + timedelta(days=14))

# ---------------------------
# BORROWED BOOKS VIEW
# ---------------------------
@app.route('/borrowed')
@login_required
def borrowed():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Update overdue status
        cursor.execute("""
            UPDATE borrow_records 
            SET status='overdue' 
            WHERE status='borrowed' AND due_date < CURRENT_DATE
        """)
        conn.commit()
        
        # Get all borrow records with details
        cursor.execute("""
            SELECT 
                br.id,
                br.book_id,
                br.member_id,
                br.borrow_date,
                br.due_date,
                br.return_date,
                br.status,
                b.title as book_title,
                b.author as book_author,
                m.name as member_name,
                m.email as member_email,
                EXTRACT(DAY FROM (CURRENT_DATE - br.due_date)) as days_overdue
            FROM borrow_records br
            JOIN books b ON br.book_id = b.id
            JOIN members m ON br.member_id = m.id
            ORDER BY br.borrow_date DESC
        """)
        records = cursor.fetchall()
        
    except Exception as e:
        print(f"❌ Borrowed page error: {e}")
        flash('Error loading borrowed books', 'error')
        records = []
    finally:
        conn.close()
    
    return render_template('borrowed.html', records=records)

# ---------------------------
# RETURN BOOK FUNCTIONALITY
# ---------------------------
@app.route('/return_book/<int:id>', methods=['POST'])
@login_required
def return_book(id):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get the borrow record
        cursor.execute("SELECT * FROM borrow_records WHERE id=%s", (id,))
        record = cursor.fetchone()
        
        if not record:
            flash('❌ Record not found!', 'error')
            conn.close()
            return redirect(url_for('borrowed'))
        
        if record['status'] == 'returned':
            flash('ℹ️ This book has already been returned.', 'info')
            conn.close()
            return redirect(url_for('borrowed'))
        
        # Process return
        cursor.execute("""
            UPDATE borrow_records 
            SET return_date=CURRENT_DATE, status='returned' 
            WHERE id=%s
        """, (id,))
        
        # Increase book quantity
        cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE id=%s", (record['book_id'],))
        
        conn.commit()
        flash('✅ Book returned successfully!', 'success')
        
    except Exception as e:
        print(f"❌ Return error: {e}")
        flash('Error returning book!', 'error')
        conn.rollback()
    finally:
        conn.close()
    
    return redirect(url_for('borrowed'))

# ---------------------------
# MEMBERS MANAGEMENT
# ---------------------------
@app.route('/members')
@login_required
def members():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT m.*, 
            (SELECT COUNT(*) FROM borrow_records WHERE member_id = m.id AND status = 'borrowed') as active_borrows
            FROM members m
            ORDER BY name
        """)
        members = cursor.fetchall()
    except Exception as e:
        print(f"❌ Members error: {e}")
        members = []
    finally:
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
            print(f"❌ Add member error: {e}")
            flash('❌ Email already exists!', 'error')
        finally:
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
        except Exception as e:
            print(f"❌ Edit member error: {e}")
            flash('❌ Email already exists!', 'error')
        finally:
            conn.close()
        return redirect(url_for('members'))
    
    try:
        cursor.execute("SELECT * FROM members WHERE id=%s", (id,))
        member = cursor.fetchone()
    except Exception as e:
        print(f"❌ Get member error: {e}")
        member = None
    finally:
        conn.close()
    
    if not member:
        flash('Member not found!', 'error')
        return redirect(url_for('members'))
    return render_template('edit_member.html', member=member)

@app.route('/delete_member/<int:id>', methods=['POST'])
@login_required
def delete_member(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM members WHERE id=%s", (id,))
        conn.commit()
        flash('🗑️ Member deleted!', 'info')
    except Exception as e:
        print(f"❌ Delete member error: {e}")
        flash('Error deleting member!', 'error')
    finally:
        conn.close()
    return redirect(url_for('members'))

# ---------------------------
# RUN APP
# ---------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
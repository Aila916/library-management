from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
import mysql.connector
from datetime import date, datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# =========================================================
# FLASK SECRET KEY
# =========================================================
app.secret_key = os.getenv(
    "SECRET_KEY",
    "library_management_secret_key_2026"
)

app.config["SESSION_PERMANENT"] = True


# =========================================================
# DATABASE CONNECTION
# =========================================================
def get_db_connection():
    config = {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "password"),
        "database": os.getenv("DB_NAME", "library_management"),
    }

    ssl_ca = os.getenv("DB_SSL_CA")

    if ssl_ca:
        if os.path.isfile(ssl_ca):
            config["ssl_ca"] = ssl_ca
        else:
            import base64
            import tempfile

            ca_path = os.path.join(
                tempfile.gettempdir(),
                "aiven-ca.pem"
            )

            try:
                ca_data = base64.b64decode(ssl_ca)

                with open(ca_path, "wb") as ca_file:
                    ca_file.write(ca_data)

                config["ssl_ca"] = ca_path

            except Exception as err:
                raise RuntimeError(
                    "Invalid Aiven CA certificate configuration."
                ) from err

    return mysql.connector.connect(**config)


# =========================================================
# LOGIN REQUIRED
# =========================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# ADMIN REQUIRED
# =========================================================
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        if session.get("role") != "admin":
            flash(
                "Access denied. Only administrators can create user accounts.",
                "danger"
            )
            return redirect(url_for("dashboard"))

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# CREATE USER ACCOUNT
# =========================================================
@app.route("/admin/create-user", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "librarian").strip().lower()

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("create_user.html")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("create_user.html")

        if role not in ["admin", "librarian"]:
            flash("Invalid user role.", "danger")
            return render_template("create_user.html")

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            )

            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username already exists.", "danger")
                return render_template("create_user.html")

            hashed_password = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s)
                """,
                (username, hashed_password, role)
            )

            conn.commit()

            flash(f"User account '{username}' created successfully.", "success")
            return redirect(url_for("create_user"))

        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Could not create user account: {err}", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template("create_user.html")


# =========================================================
# HOME
# =========================================================
@app.route("/")
@login_required
def home():
    return redirect(url_for("dashboard"))


# =========================================================
# DASHBOARD
# =========================================================
@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM books")
    total_books = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(quantity), 0) AS total FROM books")
    available = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM borrow_records
        WHERE status = 'Borrowed'
    """)
    borrowed = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM members")
    total_members = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM borrow_records
        WHERE status = 'Borrowed'
        AND due_date < CURDATE()
    """)
    overdue = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT *
        FROM books
        WHERE quantity <= 2
        ORDER BY quantity ASC
    """)
    low_stock_books = cursor.fetchall()
    low_stock_count = len(low_stock_books)

    total_fine = 0

    try:
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) AS total
            FROM fines
            WHERE status = 'Unpaid'
        """)
        result = cursor.fetchone()
        if result:
            total_fine = result["total"]
    except mysql.connector.Error:
        total_fine = 0

    cursor.execute("""
        SELECT
            br.id, br.borrow_date, br.due_date, br.return_date, br.status,
            m.fullname AS member_name,
            b.title AS book_title
        FROM borrow_records br
        JOIN members m ON br.member_id = m.id
        JOIN books b ON br.book_id = b.id
        ORDER BY br.id DESC
        LIMIT 8
    """)
    recent_activity = cursor.fetchall()

    cursor.execute("""
        SELECT
            MONTH(borrow_date) AS month_number,
            MONTHNAME(borrow_date) AS month_name,
            COUNT(*) AS total
        FROM borrow_records
        WHERE YEAR(borrow_date) = YEAR(CURDATE())
        GROUP BY MONTH(borrow_date), MONTHNAME(borrow_date)
        ORDER BY MONTH(borrow_date)
    """)
    monthly_borrowing = cursor.fetchall()

    cursor.execute("""
        SELECT category, COUNT(*) AS total
        FROM books
        GROUP BY category
        ORDER BY total DESC
    """)
    books_by_category = cursor.fetchall()

    cursor.execute("""
        SELECT b.title, b.author, COUNT(br.id) AS borrow_count
        FROM books b
        LEFT JOIN borrow_records br ON b.id = br.book_id
        GROUP BY b.id, b.title, b.author
        ORDER BY borrow_count DESC
        LIMIT 5
    """)
    most_borrowed = cursor.fetchall()

    cursor.execute("""
        SELECT m.fullname, COUNT(br.id) AS borrow_count
        FROM members m
        LEFT JOIN borrow_records br ON m.id = br.member_id
        GROUP BY m.id, m.fullname
        ORDER BY borrow_count DESC
        LIMIT 5
    """)
    most_active_members = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM borrow_records
        WHERE return_date IS NOT NULL
    """)
    returned_count = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM borrow_records
        WHERE return_date IS NOT NULL
        AND return_date <= due_date
    """)
    on_time_returns = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM borrow_records
        WHERE return_date IS NOT NULL
        AND return_date > due_date
    """)
    late_returns = cursor.fetchone()["total"]

    current_overdue = overdue

    cursor.execute("""
        SELECT COALESCE(AVG(DATEDIFF(return_date, due_date)), 0) AS average_days
        FROM borrow_records
        WHERE return_date IS NOT NULL
        AND return_date > due_date
    """)
    average_result = cursor.fetchone()
    avg_late_days = round(float(average_result["average_days"] or 0), 1)

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_books=total_books,
        available=available,
        borrowed=borrowed,
        total_members=total_members,
        overdue=overdue,
        total_fine=total_fine,
        low_stock_count=low_stock_count,
        low_stock_books=low_stock_books,
        recent_activity=recent_activity,
        most_active_members=most_active_members,
        low_stock=low_stock_books,
        recent=recent_activity,
        active_members=most_active_members,
        monthly_borrowing=monthly_borrowing,
        books_by_category=books_by_category,
        most_borrowed=most_borrowed,
        returned_count=returned_count,
        on_time_returns=on_time_returns,
        late_returns=late_returns,
        current_overdue=current_overdue,
        avg_late_days=avg_late_days
    )


# =========================================================
# LOGIN
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                """
                SELECT id, username, password, role
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            user = cursor.fetchone()

            if not user:
                flash("Invalid username or password.", "danger")
                return render_template("login.html")

            stored_password = str(user["password"])
            password_valid = False

            if stored_password == password:
                password_valid = True
            else:
                try:
                    password_valid = check_password_hash(stored_password, password)
                except (ValueError, TypeError):
                    password_valid = False

            if password_valid:
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                session.permanent = True

                flash("Login successful.", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid username or password.", "danger")

        except mysql.connector.Error as e:
            flash(f"Database error: {e}", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


# =========================================================
# BOOKS
# =========================================================
@app.route("/books")
@login_required
def books():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM books ORDER BY id DESC")
    books_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("books.html", books=books_list)


# =========================================================
# ADD BOOK
# =========================================================
@app.route("/books/add", methods=["GET", "POST"])
@login_required
def add_book():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", 0)

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO books (title, author, isbn, category, quantity)
                VALUES (%s, %s, %s, %s, %s)
            """, (title, author, isbn, category, quantity))

            conn.commit()
            flash("Book added successfully.", "success")

        except mysql.connector.Error as e:
            conn.rollback()
            flash(f"Error adding book: {e}", "danger")

        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("books"))

    return render_template("add_book.html")


# =========================================================
# EDIT BOOK
# =========================================================
@app.route("/books/edit/<int:book_id>", methods=["GET", "POST"])
@login_required
def edit_book(book_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()
        category = request.form.get("category", "").strip()
        quantity = request.form.get("quantity", 0)

        cursor.execute("""
            UPDATE books
            SET title = %s, author = %s, isbn = %s, category = %s, quantity = %s
            WHERE id = %s
        """, (title, author, isbn, category, quantity, book_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Book updated successfully.", "success")
        return redirect(url_for("books"))

    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_book.html", book=book)


# =========================================================
# DELETE BOOK
# =========================================================
@app.route("/books/delete/<int:book_id>")
@login_required
def delete_book(book_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
        conn.commit()
        flash("Book deleted successfully.", "success")

    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Cannot delete this book: {e}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("books"))


# =========================================================
# MEMBERS
# =========================================================
@app.route("/members")
@login_required
def members():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM members ORDER BY id DESC")
    members_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("members.html", members=members_list)


# =========================================================
# ADD MEMBER
# =========================================================
@app.route("/members/add", methods=["GET", "POST"])
@login_required
def add_member():

    if request.method == "POST":

        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO members (fullname, email, phone)
                VALUES (%s, %s, %s)
            """, (fullname, email, phone))

            conn.commit()
            flash("Member added successfully.", "success")

        except mysql.connector.Error as e:
            conn.rollback()
            flash(f"Error adding member: {e}", "danger")

        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("members"))

    return render_template("add_member.html")


# =========================================================
# EDIT MEMBER
# =========================================================
@app.route("/members/edit/<int:member_id>", methods=["GET", "POST"])
@login_required
def edit_member(member_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()

        cursor.execute("""
            UPDATE members
            SET fullname = %s, email = %s, phone = %s
            WHERE id = %s
        """, (fullname, email, phone, member_id))

        conn.commit()
        cursor.close()
        conn.close()

        flash("Member updated successfully.", "success")
        return redirect(url_for("members"))

    cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
    member = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("edit_member.html", member=member)


# =========================================================
# DELETE MEMBER
# =========================================================
@app.route("/members/delete/<int:member_id>")
@login_required
def delete_member(member_id):

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
        conn.commit()
        flash("Member deleted successfully.", "success")

    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Cannot delete member: {e}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("members"))


# =========================================================
# BORROW BOOK
# =========================================================
@app.route("/borrow", methods=["GET", "POST"])
@login_required
def borrow_book():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        member_id = request.form.get("member_id")
        book_id = request.form.get("book_id")
        due_date = request.form.get("due_date")

        try:
            cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
            book = cursor.fetchone()

            if not book:
                flash("Book not found.", "danger")

            elif book["quantity"] <= 0:
                flash("This book is currently out of stock.", "danger")

            else:
                cursor.execute("SELECT * FROM members WHERE id = %s", (member_id,))
                member = cursor.fetchone()

                if not member:
                    flash("Member not found.", "danger")

                else:
                    cursor.execute("""
                        INSERT INTO borrow_records
                        (member_id, book_id, borrow_date, due_date, status)
                        VALUES (%s, %s, CURDATE(), %s, 'Borrowed')
                    """, (member_id, book_id, due_date))

                    cursor.execute("""
                        UPDATE books SET quantity = quantity - 1
                        WHERE id = %s
                    """, (book_id,))

                    conn.commit()
                    flash("Book borrowed successfully.", "success")

                    cursor.close()
                    conn.close()

                    return redirect(url_for("borrowed_books"))

        except mysql.connector.Error as e:
            conn.rollback()
            flash(f"Borrowing error: {e}", "danger")

    cursor.execute("SELECT * FROM books WHERE quantity > 0 ORDER BY title")
    books_list = cursor.fetchall()

    cursor.execute("SELECT * FROM members ORDER BY fullname")
    members_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "borrow_book.html",
        books=books_list,
        members=members_list
    )


# =========================================================
# BORROWED BOOKS
# =========================================================
@app.route("/borrowed")
@login_required
def borrowed_books():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            br.*,
            m.fullname AS member_name,
            m.email,
            b.title AS book_title,
            b.author
        FROM borrow_records br
        JOIN members m ON br.member_id = m.id
        JOIN books b ON br.book_id = b.id
        WHERE br.status = 'Borrowed'
        ORDER BY br.id DESC
    """)

    records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "borrowed.html",
        records=records,
        today=date.today()
    )


# =========================================================
# RETURN BOOK
# =========================================================
@app.route("/return/<int:record_id>")
@login_required
def return_book(record_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM borrow_records WHERE id = %s", (record_id,))
        record = cursor.fetchone()

        if not record:
            flash("Borrow record not found.", "danger")

        elif record["status"] == "Returned":
            flash("This book has already been returned.", "warning")

        else:
            cursor.execute("""
                UPDATE borrow_records
                SET return_date = CURDATE(), status = 'Returned'
                WHERE id = %s
            """, (record_id,))

            cursor.execute("""
                UPDATE books SET quantity = quantity + 1
                WHERE id = %s
            """, (record["book_id"],))

            conn.commit()
            flash("Book returned successfully.", "success")

    except mysql.connector.Error as e:
        conn.rollback()
        flash(f"Return error: {e}", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for("borrowed_books"))


# =========================================================
# OVERDUE BOOKS
# =========================================================
@app.route("/overdue")
@login_required
def overdue_books():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            br.*,
            m.fullname AS member_name,
            m.phone,
            b.title AS book_title,
            b.author,
            DATEDIFF(CURDATE(), br.due_date) AS days_overdue
        FROM borrow_records br
        JOIN members m ON br.member_id = m.id
        JOIN books b ON br.book_id = b.id
        WHERE br.status = 'Borrowed'
        AND br.due_date < CURDATE()
        ORDER BY br.due_date ASC
    """)

    overdue_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("overdue.html", overdue=overdue_list)


# =========================================================
# BORROWING HISTORY
# =========================================================
@app.route("/borrow-history")
@login_required
def borrow_history():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            br.*,
            m.fullname AS member_name,
            m.email,
            b.title AS book_title,
            b.author
        FROM borrow_records br
        JOIN members m ON br.member_id = m.id
        JOIN books b ON br.book_id = b.id
        ORDER BY br.id DESC
    """)

    history = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("borrow_history.html", history=history)


# =========================================================
# FINES (list)
# =========================================================
@app.route("/fines")
@login_required
def fines():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    unpaid_fines = []
    paid_fines = []

    try:
        cursor.execute("""
            SELECT br.id, br.due_date, br.return_date, br.status,
                   m.fullname AS member_name,
                   b.title AS book_title,
                   CASE
                       WHEN br.return_date IS NOT NULL
                           THEN DATEDIFF(br.return_date, br.due_date)
                       ELSE DATEDIFF(CURDATE(), br.due_date)
                   END AS days_overdue,
                   CASE
                       WHEN br.return_date IS NOT NULL
                           THEN DATEDIFF(br.return_date, br.due_date) * 10
                       ELSE DATEDIFF(CURDATE(), br.due_date) * 10
                   END AS amount
            FROM borrow_records br
            JOIN members m ON br.member_id = m.id
            JOIN books b ON br.book_id = b.id
            WHERE br.due_date < CURDATE()
            AND (br.fine_paid IS NULL OR br.fine_paid = 0)
            AND (
                (br.status = 'Borrowed' AND br.due_date < CURDATE())
                OR
                (br.status = 'Returned' AND br.return_date > br.due_date)
            )
            ORDER BY br.due_date ASC
        """)
        unpaid_fines = cursor.fetchall()

    except mysql.connector.Error:
        unpaid_fines = []

    try:
        cursor.execute("SELECT * FROM payments ORDER BY payment_date DESC")
        paid_fines = cursor.fetchall()

    except mysql.connector.Error:
        paid_fines = []

    cursor.close()
    conn.close()

    return render_template(
        "fines.html",
        fines=unpaid_fines,
        paid_fines=paid_fines
    )


# =========================================================
# PAY FINE
# =========================================================
@app.route("/fines/pay/<int:record_id>", methods=["GET", "POST"])
@login_required
def pay_fine(record_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT br.*,
               m.id AS member_id,
               m.fullname AS member_name,
               m.email,
               m.phone,
               b.title AS book_title,
               CASE
                   WHEN br.return_date IS NOT NULL
                       THEN DATEDIFF(br.return_date, br.due_date)
                   ELSE DATEDIFF(CURDATE(), br.due_date)
               END AS days_overdue,
               CASE
                   WHEN br.return_date IS NOT NULL
                       THEN DATEDIFF(br.return_date, br.due_date) * 10
                   ELSE DATEDIFF(CURDATE(), br.due_date) * 10
               END AS amount
        FROM borrow_records br
        JOIN members m ON br.member_id = m.id
        JOIN books b ON br.book_id = b.id
        WHERE br.id = %s
    """, (record_id,))

    fine = cursor.fetchone()

    if not fine:
        flash("Borrow record not found.", "danger")
        cursor.close()
        conn.close()
        return redirect(url_for("fines"))

    if request.method == "POST":

        payment_method = request.form.get("payment_method", "Cash")
        receipt_number = request.form.get("receipt_number", "").strip()

        if not receipt_number:
            receipt_number = "RCP-" + datetime.now().strftime("%Y%m%d%H%M%S")

        try:
            cursor.execute("""
                INSERT INTO payments
                (fine_id, borrow_record_id, member_id, amount,
                 payment_method, receipt_number, received_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                record_id,
                record_id,
                fine["member_id"],
                fine["amount"],
                payment_method,
                receipt_number,
                session.get("username", "System")
            ))

            cursor.execute("""
                UPDATE borrow_records SET fine_paid = 1
                WHERE id = %s
            """, (record_id,))

            conn.commit()

            flash(
                f"Payment of KES {fine['amount']} received successfully. "
                f"Receipt: {receipt_number}",
                "success"
            )

            payment_id = cursor.lastrowid
            cursor.close()
            conn.close()

            return redirect(url_for("payment_receipt", payment_id=payment_id))

        except mysql.connector.Error as e:
            conn.rollback()
            flash(f"Payment error: {e}", "danger")

    cursor.close()
    conn.close()

    return render_template("pay_fine.html", fine=fine)


# =========================================================
# PAYMENT RECEIPT
# =========================================================
@app.route("/payments/receipt/<int:payment_id>")
@login_required
def payment_receipt(payment_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.*,
               m.fullname AS member_name,
               m.email,
               m.phone,
               b.title AS book_title
        FROM payments p
        JOIN members m ON p.member_id = m.id
        JOIN borrow_records br ON p.borrow_record_id = br.id
        JOIN books b ON br.book_id = b.id
        WHERE p.id = %s
    """, (payment_id,))

    payment = cursor.fetchone()

    cursor.close()
    conn.close()

    if not payment:
        flash("Payment record not found.", "danger")
        return redirect(url_for("fines"))

    return render_template("payment_receipt.html", payment=payment)


# =========================================================
# LOW STOCK
# =========================================================
@app.route("/low-stock")
@login_required
def low_stock():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM books
        WHERE quantity <= 2
        ORDER BY quantity ASC
    """)

    books_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("low_stock.html", books=books_list)


# =========================================================
# SEARCH
# =========================================================
@app.route("/search")
@login_required
def search():

    query = request.args.get("q", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if query:
        search_value = f"%{query}%"
        cursor.execute("""
            SELECT * FROM books
            WHERE title LIKE %s
               OR author LIKE %s
               OR isbn LIKE %s
               OR category LIKE %s
            ORDER BY title
        """, (search_value, search_value, search_value, search_value))
    else:
        cursor.execute("SELECT * FROM books ORDER BY title")

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("search.html", results=results, query=query)


# =========================================================
# BOOK SUGGESTIONS
# =========================================================
@app.route("/book-suggestions")
@login_required
def book_suggestions():

    query = request.args.get("q", "").strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    search_value = f"%{query}%"

    cursor.execute("""
        SELECT id, title, author, isbn, category
        FROM books
        WHERE title LIKE %s
           OR author LIKE %s
           OR isbn LIKE %s
        ORDER BY title
        LIMIT 10
    """, (search_value, search_value, search_value))

    books_list = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(books_list)


# =========================================================
# PROFILE
# =========================================================
@app.route("/profile")
@login_required
def profile():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id = %s", (session["user_id"],))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("profile.html", user=user)


# =========================================================
# REPORTS
# =========================================================
@app.route("/reports")
@login_required
def reports():
    return render_template("reports.html")


# =========================================================
# ERROR HANDLERS
# =========================================================
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500


# =========================================================
# RUN APPLICATION
# =========================================================
if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from datetime import date, timedelta, datetime
from functools import wraps
import re
import traceback
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database connection
def get_db_connection():
    if os.environ.get('RENDER'):
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', 'password'),
            database=os.environ.get('DB_NAME', 'sale')
        )
    else:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="sale"
        )
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first!', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Add your routes here (dashboard, books, borrow_book, etc.)
# Copy all your route functions from your current app.py

# At the very bottom - this is where the error was
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
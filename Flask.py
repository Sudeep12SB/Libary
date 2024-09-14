from flask import Flask, request, jsonify, render_template
import sqlite3
from datetime import datetime, timedelta
import random

app = Flask(__name__)

# Database connection function
def connect_db():
    conn = sqlite3.connect('library.db')
    return conn

# Initialize database
def init_db():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            branch TEXT NOT NULL,
            reg_no INTEGER NOT NULL
        );''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            is_available BOOLEAN NOT NULL DEFAULT 1
        );''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS borrowed_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date DATE,
            return_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (book_id) REFERENCES books(id)
        );''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register_user():
    name = request.form['name']
    branch = request.form['branch']
    reg_no = request.form['reg_no']
    
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, branch, reg_no) VALUES (?, ?, ?)", (name, branch, reg_no))
        conn.commit()
        
    return jsonify({'status': 'success', 'message': f'Registered {name}'})

@app.route('/available_books', methods=['GET'])
def available_books():
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM books WHERE is_available = 1")
        books = cursor.fetchall()
    return jsonify({'available_books': [book[0] for book in books]})

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO books (title) VALUES (?)", (title,))
        conn.commit()
    
    return jsonify({'status': 'success', 'message': f'Added book {title}'})

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    user_id = request.form['user_id']
    book_title = request.form['book_title']
    
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM books WHERE title = ? AND is_available = 1", (book_title,))
        book = cursor.fetchone()
        
        if book:
            book_id = book[0]
            cursor.execute("UPDATE books SET is_available = 0 WHERE id = ?", (book_id,))
            borrow_date = datetime.now().date()
            return_date = borrow_date + timedelta(days=15)  # 15 days to return
            cursor.execute("INSERT INTO borrowed_books (user_id, book_id, borrow_date, return_date) VALUES (?, ?, ?, ?)",
                           (user_id, book_id, borrow_date, return_date))
            conn.commit()
            return jsonify({'status': 'success', 'message': f'Borrowed book {book_title}', 'return_date': return_date})
        else:
            return jsonify({'status': 'error', 'message': f'Book {book_title} is not available'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

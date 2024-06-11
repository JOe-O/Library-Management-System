from flask import Flask, render_template, request, redirect, url_for, session,jsonify
import mysql.connector
from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = 'abcd12345'  

app.config['SESSION_PERMANENT'] = False

def create_connection():
    connection = mysql.connector.connect(
        host='172.17.0.4',
        user='root',
        password='',
        database='library'
    )
    return connection

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("select * from users where username= %s and password= %s",(username,password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]
            # session.permanent = False
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html',message='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('login'))  # Redirect to the login page


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    print("user info",user[0])
    cursor.close()
    connection.close()

    return render_template('dashboard.html', user=user)

@app.route('/books')
def books():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('books.html', books=books)

@app.route('/dashboard_main')
def main_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    connection = create_connection()
    cursor = connection.cursor()

    # Retrieve user information
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    # Retrieve counts
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM books WHERE available = 1")
    available_books = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM borrowers")
    total_borrowed_books = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template('dashboard_main.html', user=user, total_books=total_books, available_books=available_books, total_users=total_users, total_borrowed_books=total_borrowed_books)

@app.route('/users')
def users():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('users.html',users=users)

@app.route('/borrowed_books')
def borrowed_books():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM borrowers")
    borrowers = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('borrowed_books.html',borrowers=borrowers)

@app.route('/edit_book/<int:book_id>', methods=['GET'])
def edit_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
    role = cursor.fetchone()

    if not role or role[0] != 'admin':
        return jsonify({'message': 'Only admin users can edit books'}), 401

    cursor.execute("SELECT * FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('edit_book.html', book=book)

@app.route('/update_book/<int:book_id>', methods=['POST'])
def update_book(book_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    author = request.form['author']
    isbn = request.form['isbn']
    available = 1 if 'available' in request.form else 0

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE books
        SET title = %s, author = %s, isbn = %s, available = %s
        WHERE id = %s
    """, (title, author, isbn, available, book_id))
    connection.commit()
    cursor.close()
    connection.close()

    return redirect(url_for('dashboard'))

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        isbn = request.form['isbn']
        available = 1 if 'available' in request.form else 0

        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO books (title, author, isbn, available)
            VALUES (%s, %s, %s, %s)
        """, (title, author, isbn, available))
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('books'))

    return render_template('add_book.html')

@app.route('/borrow/<int:book_id>', methods=['POST'])
def borrow_book(book_id):
    if 'user_id' not in session:
        return jsonify({'message': 'You must be logged in to borrow a book'}), 401

    user_id = session['user_id']

    connection = create_connection()
    cursor = connection.cursor()

    # Check if the book is available
    cursor.execute("SELECT available FROM books WHERE id = %s", (book_id,))
    book_available = cursor.fetchone()

    if not book_available or book_available[0] == 0:
        cursor.close()
        connection.close()
        return jsonify({'message': 'The book is not available for borrowing'}), 400

    # Update the book's availability
    cursor.execute("UPDATE books SET available = 0 WHERE id = %s", (book_id,))

    # Add the book to the borrower's table
    borrow_date = datetime.now().date()
    return_date = borrow_date + timedelta(days=14)  # Assuming a 14-day borrowing period
    cursor.execute("INSERT INTO borrowers (user_id, book_id, borrow_date, return_date) VALUES (%s, %s, %s, %s)",
                   (user_id, book_id, borrow_date, return_date))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'message': 'Book borrowed successfully'}), 200

@app.route('/change_password/<int:user_id>', methods=['GET', 'POST'])
def change_password(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['password']
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_password, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('dashboard'))

    return render_template('change_pass.html',user_id=user_id)

@app.route('/change_role/<int:user_id>', methods=['GET', 'POST'])
def change_role(user_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_role = request.form['role']
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("UPDATE users SET role = %s WHERE id = %s", (new_role, user_id))
        connection.commit()
        cursor.close()
        connection.close()
        return redirect(url_for('dashboard'))

    return render_template('change_role.html', user_id=user_id)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        newUser = request.form['username']
        newPass = request.form['password']
        connection = create_connection()
        cursor = connection.cursor()

        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username = %s", (newUser,))
        existing_user = cursor.fetchone()

        if existing_user:
            # Close the connection
            cursor.close()
            connection.close()
            return render_template('add_user.html', error="Username already exists")
        else:
            # Insert the new user
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (newUser, newPass))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('dashboard'))

    return render_template('add_user.html')



@app.route('/test_database')
def test_database():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(users)


if __name__ == '__main__':
    app.run(debug=True,port=5000)
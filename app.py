from flask import Flask, request, render_template_string,g
import sqlite3

app = Flask(__name__)

def init_db():
    with app.app_context():
        db = get_db()
        # Create the users table
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            );
        ''')
        # Insert a demo user
        db.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', 'password123'))
        db.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('users.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def login():
    return render_template_string('''
        <form action="/login" method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    ''')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    db = get_db()
    cursor = db.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return "Logged in successfully!"
    else:
        return "Failed to log in!"

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run()

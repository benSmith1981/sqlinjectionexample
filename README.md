Here is an explanation of the concept of an SQL injection and provide a safe example of how an SQL injection vulnerability might occur, along with how to prevent it.

**Hypothetical Vulnerable Flask Application with SQLite:**

Let's assume you have a Flask application with a login form that queries an SQLite database to authenticate users. Here's a simplified example of how an SQL injection vulnerability could be introduced:

```python
# app.py
from flask import Flask, request, render_template_string
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

```

In the above example, the `do_login` function directly interpolates the `username` and `password` into the SQL query without any validation or sanitization. This is a classic example of a code that is vulnerable to SQL injection.

**How SQL Injection Might Occur:**

An attacker could submit the following as the username: `admin' --`. The resulting query would look like this:

```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = ''
```

The `--` is a comment in SQL, which effectively nullifies the rest of the query, bypassing the password check and potentially allowing unauthorized access.

**How to Prevent SQL Injection:**

To prevent SQL injections, you should use parameterized queries or prepared statements:

```python
@app.route('/login', methods=['POST'])
def do_login_safe():
    username = request.form['username']
    password = request.form['password']
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    result = cursor.fetchone()
    if result:
        return "Logged in successfully!"
    else:
        return "Failed to log in!"
```

By using parameterized queries, you're asking the database to handle the input as data only, not part of the

SQL command, thus preventing any embedded SQL within the input from being executed as part of the command. The database understands the placeholders `?` as parameters whose values are provided in the tuple `(username, password)`.

This approach ensures that the user input is never treated as an executable part of the SQL command, effectively mitigating the risk of SQL injection.

For educational purposes, one can demonstrate the vulnerability using the first example and then show the safer method using parameterized queries. It's crucial to emphasize that vulnerabilities should never be left in live code, and security best practices should always be followed when developing applications.

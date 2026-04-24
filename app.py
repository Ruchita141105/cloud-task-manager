from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()

    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        status INTEGER
    )''')

    db.commit()

# Call DB init at startup (IMPORTANT for Render)
init_db()

# ---------------- AUTH ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, password))
            db.commit()
            return redirect('/login')
        except:
            return "User already exists"

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session['user_id'] = user['id']
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------------- TASKS ----------------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    db = get_db()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id=?",
        (session['user_id'],)
    ).fetchall()

    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
def add():
    if 'user_id' not in session:
        return redirect('/login')

    task = request.form['task']

    db = get_db()
    db.execute(
        "INSERT INTO tasks (user_id, content, status) VALUES (?, ?, ?)",
        (session['user_id'], task, 0)
    )
    db.commit()

    return redirect('/')


@app.route('/complete/<int:id>')
def complete(id):
    db = get_db()
    db.execute("UPDATE tasks SET status=1 WHERE id=?", (id,))
    db.commit()
    return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=?", (id,))
    db.commit()
    return redirect('/')


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()

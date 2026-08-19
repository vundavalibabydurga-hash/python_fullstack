import sqlite3
# pyrefly: ignore [missing-import]
from flask import Flask,render_template,jsonify,request,redirect,url_for,session
#pyrefly:ignore [miing-import]
from werkzeug.security import check_password_hash
app = Flask(__name__)
app.secret_key="super_secret_key"

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    # return row as dictionary 
    return conn
 
# create database tables
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        dob TEXT NOT NULL,
        gender TEXT NOT NULL,
        course TEXT NOT NULL
    )
    """)
    # create tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'pending',
        due_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_email) REFERENCES users(email)
    )
    """)
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/courses')
def courses():
    return render_template("courses.html")

@app.route('/trainers')
def trainers():
    return render_template("trainers.html")

@app.route('/register',methods=["POST","GET"])
def register():
    return render_template("register.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    return render_template("login.html")

@app.route('/tasks')
def tasks():
    if not session.get('user_email'):
        return redirect(url_for('login'))
    return render_template("task.html")

@app.route('/api/register', methods=["POST"])
def api_register():
    data = request.get_json()
    email = data.get("email")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if user:
        return jsonify({"status": "error", "message": "User already exists with this email!"}), 400
    
    cursor.execute("INSERT INTO users (name, email, password, dob, gender, course) VALUES (?, ?, ?, ?, ?, ?)", (data["name"], data["email"], data["password"], data["dob"], data["gender"], data["course"]))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Registration successful!"})

@app.route('/api/login', methods=["POST"])
def api_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user and user["password"] == password:
        session['user_email'] = user["email"]
        session['user_name'] = user["name"]
        return jsonify({"status": "success", "message": "Login successful! Welcome back."})
    else:
        return jsonify({"status": "error", "message": "Invalid email or password!"}), 401

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    return redirect(url_for('home'))

# Task Management API Endpoints

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    if not session.get('user_email'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    
    user_email = session.get('user_email')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE user_email = ? ORDER BY created_at DESC", (user_email,))
    tasks_data = cursor.fetchall()
    conn.close()
    
    tasks_list = [dict(task) for task in tasks_data]
    return jsonify({"status": "success", "tasks": tasks_list})

@app.route('/api/tasks', methods=['POST'])
def add_task():
    if not session.get('user_email'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    
    data = request.get_json()
    user_email = session.get('user_email')
    title = data.get('title')
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    due_date = data.get('due_date', '')
    
    if not title or not title.strip():
        return jsonify({"status": "error", "message": "Task title is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (user_email, title, description, priority, due_date) VALUES (?, ?, ?, ?, ?)",
        (user_email, title, description, priority, due_date)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    return jsonify({"status": "success", "message": "Task added successfully", "task_id": task_id})

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    if not session.get('user_email'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    
    user_email = session.get('user_email')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if task belongs to user
    cursor.execute("SELECT * FROM tasks WHERE id = ? AND user_email = ?", (task_id, user_email))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "Task not found or not authorized"}), 404
    
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    due_date = data.get('due_date', '')
    
    if not title or not title.strip():
        conn.close()
        return jsonify({"status": "error", "message": "Task title is required"}), 400
    
    cursor.execute(
        "UPDATE tasks SET title = ?, description = ?, priority = ?, due_date = ? WHERE id = ?",
        (title, description, priority, due_date, task_id)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Task updated successfully"})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    if not session.get('user_email'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    
    user_email = session.get('user_email')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if task belongs to user
    cursor.execute("SELECT * FROM tasks WHERE id = ? AND user_email = ?", (task_id, user_email))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "Task not found or not authorized"}), 404
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Task deleted successfully"})

@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    if not session.get('user_email'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    
    user_email = session.get('user_email')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if task belongs to user
    cursor.execute("SELECT * FROM tasks WHERE id = ? AND user_email = ?", (task_id, user_email))
    if not cursor.fetchone():
        conn.close()
        return jsonify({"status": "error", "message": "Task not found or not authorized"}), 404
    
    cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Task marked as completed"})

if __name__ == '__main__':
    app.run(debug=True)
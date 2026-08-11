import os
import sqlite3

from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                dob TEXT,
                gender TEXT,
                course TEXT
            )
            """
        )
        conn.commit()


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
    if request.method=="POST":
        name=request.form["name"]
        email=request.form["email"]
        password=request.form["password"]
        dob=request.form["dob"]
        gender=request.form["gender"]
        course=request.form["course"]
        return render_template("register.html")
    return render_template("register.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        return render_template("login.html")
    return render_template("login.html")

@app.route('/api/register', methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()

    if not email:
        return jsonify({"status": "error", "message": "Email is required!"}), 400

    with get_db_connection() as conn:
        existing_user = conn.execute(
            "SELECT 1 FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            return jsonify({"status": "error", "message": "User already exists with this email!"}), 400

        conn.execute(
            """
            INSERT INTO users (name, email, password, dob, gender, course)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                data.get("name"),
                email,
                data.get("password"),
                data.get("dob"),
                data.get("gender"),
                data.get("course")
            )
        )
        conn.commit()

    return jsonify({"status": "success", "message": "Registration successful!"})


@app.route('/api/login', methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    with get_db_connection() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

    if user:
        return jsonify({"status": "success", "message": "Login successful! Welcome back."})
    return jsonify({"status": "error", "message": "Invalid email or password!"}), 401

if __name__ == '__main__':
    app.run(debug=True)
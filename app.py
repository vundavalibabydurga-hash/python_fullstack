from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"


# Database connection
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# Home
@app.route("/")
def home():
    return render_template("index.html")


# Login
@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")



# Register
@app.route("/register", methods=["POST", "GET"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        dob = request.form["dob"]
        gender = request.form["gender"]
        course = request.form["course"]

        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO users
                (name, email, password, dob, gender, course)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    name,
                    email,
                    password,
                    dob,
                    gender,
                    course
                )
            )
            conn.commit()

        return jsonify({
            "status": "success",
            "message": "Registration successful!"
        })

    return render_template("register.html")


# API Login
@app.route("/api/login", methods=["POST"])
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
        session["user_email"] = user["email"]
        session["user_name"] = user["name"]

        return jsonify({
            "status": "success",
            "message": "Login successful! Welcome back."
        })

    return jsonify({
        "status": "error",
        "message": "Invalid email or password!"
    }), 401

@app.route('/logout', methods=["GET"])
def logout():
    session.pop("user_email", None)
    session.pop("user_name", None)
    return redirect(url_for("home"))


# Run application
if __name__ == "__main__":
    app.run(debug=True)
    
    

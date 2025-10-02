from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session management

DB_FILE = "app.db"

# -------------------------------
# Database setup
# -------------------------------
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    owner_id INTEGER,
    FOREIGN KEY (owner_id) REFERENCES users(id)
)
""")
conn.commit()

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Username already exists!"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            session["user_id"] = user[0]
            return redirect(url_for("dashboard"))
        else:
            return "Incorrect username or password!"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    cursor.execute("SELECT id, name FROM items WHERE owner_id=?", (user_id,))
    items = cursor.fetchall()
    return render_template("dashboard.html", items=items)

@app.route("/create", methods=["POST"])
def create():
    if "user_id" in session:
        name = request.form["name"]
        user_id = session["user_id"]
        cursor.execute("INSERT INTO items (name, owner_id) VALUES (?, ?)", (name, user_id))
        conn.commit()
    return redirect(url_for("dashboard"))

@app.route("/delete/<int:item_id>")
def delete(item_id):
    if "user_id" in session:
        user_id = session["user_id"]
        cursor.execute("DELETE FROM items WHERE id=? AND owner_id=?", (item_id, user_id))
        conn.commit()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    is_production = os.environ.get("ENV") == "production"
    app.run(host="0.0.0.0", port=5000, debug=not is_production)



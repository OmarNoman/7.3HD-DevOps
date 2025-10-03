from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Default DB path (can be overridden)
DB_PATH = os.environ.get("DB_FILE", "python_login_webapp/app.db")


def connect_db():
    """Create a new database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def setup_db():
    """Create tables if they don’t exist."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()


# Run once on startup
setup_db()


# ---------------- Routes ----------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = connect_db()
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return "Username already exists!"
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = connect_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM users WHERE username=? AND password=?",
            (username, password),
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        return "Incorrect username or password!"
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items WHERE owner_id=?", (session["user_id"],))
    items = cur.fetchall()
    conn.close()
    return render_template("dashboard.html", items=items)


@app.route("/create", methods=["POST"])
def create():
    if "user_id" in session:
        conn = connect_db()
        conn.execute(
            "INSERT INTO items (name, owner_id) VALUES (?, ?)",
            (request.form["name"], session["user_id"]),
        )
        conn.commit()
        conn.close()
    return redirect(url_for("dashboard"))


@app.route("/delete/<int:item_id>")
def delete(item_id):
    if "user_id" in session:
        conn = connect_db()
        conn.execute(
            "DELETE FROM items WHERE id=? AND owner_id=?",
            (item_id, session["user_id"]),
        )
        conn.commit()
        conn.close()
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    prod = os.environ.get("ENV") == "production"
    app.run(host="0.0.0.0", port=5000, debug=not prod)

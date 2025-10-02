import pytest
import sqlite3
from flask import session
from python_login_webapp.app import app

# -------------------------------
# Configure app for testing
# -------------------------------
@pytest.fixture(scope="function")
def test_client():
    # Use Flask test client
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Use in-memory SQLite DB
    app.config["DB_FILE"] = ":memory:"

    # Recreate tables in-memory
    conn = sqlite3.connect(app.config["DB_FILE"])
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            owner_id INTEGER,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client

# -------------------------------
# Tests
# -------------------------------

def test_register_login_logout(test_client):
    # Register
    rv = test_client.post("/register", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert rv.status_code == 200

    # Login
    rv = test_client.post("/login", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert b"Your Items" in rv.data  # Dashboard content

    # Logout
    rv = test_client.get("/logout", follow_redirects=True)
    assert rv.status_code == 200
    assert b"Register" in rv.data or b"Login" in rv.data

def test_create_and_delete_item(test_client):
    # Register & login
    test_client.post("/register", data={"username": "user2", "password": "pass"})
    test_client.post("/login", data={"username": "user2", "password": "pass"})

    # Create item
    rv = test_client.post("/create", data={"name": "Item1"}, follow_redirects=True)
    assert b"Item1" in rv.data

    # Delete item
    rv = test_client.get("/delete/1", follow_redirects=True)
    assert b"Item1" not in rv.data

def test_index_page(test_client):
    rv = test_client.get("/")
    assert rv.status_code == 200
    assert b"Register" in rv.data or b"Login" in rv.data

def test_dashboard_requires_login(test_client):
    rv = test_client.get("/dashboard", follow_redirects=True)
    assert b"Login" in rv.data

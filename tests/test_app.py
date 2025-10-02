import sys
sys.path.append("/app/python_login_webapp")
import pytest
import os
os.environ["DB_FILE"] = ":memory:"
import sqlite3
from app import app, DB_FILE

# -------------------------------
# Setup test database
# -------------------------------
@pytest.fixture(scope="module")
def test_client():
    # Use Flask test client
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    testing_client = app.test_client()

    # Create fresh test database
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
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

    yield testing_client

    # Cleanup DB after tests
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

# -------------------------------
# Tests
# -------------------------------

def test_register_login_logout(test_client):
    # Register
    response = test_client.post("/register", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert b"login" in response.data or response.status_code == 200

    # Login
    response = test_client.post("/login", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert b"dashboard" in response.data or response.status_code == 200

    # Logout
    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"index" in response.data

def test_create_and_delete_item(test_client):
    # Login first
    test_client.post("/register", data={"username": "user2", "password": "pass"})
    test_client.post("/login", data={"username": "user2", "password": "pass"})

    # Create item
    response = test_client.post("/create", data={"name": "Item1"}, follow_redirects=True)
    assert b"Item1" in response.data

    # Delete item
    response = test_client.get("/delete/1", follow_redirects=True)
    assert b"Item1" not in response.data

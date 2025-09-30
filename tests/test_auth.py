import sqlite3
import pytest
from main import register, login, create_item, read_items, update_item, delete_item

# Use an in-memory SQLite database for testing
@pytest.fixture
def db_connection(monkeypatch):
    # Patch sqlite3.connect to use in-memory database
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create tables
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

    # Patch the original connection in main.py
    monkeypatch.setattr("main.conn", conn)
    monkeypatch.setattr("main.cursor", cursor)

    yield cursor, conn

# -------------------------------
# Helper functions to bypass input/getpass
# -------------------------------
def mock_register(username, password, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: username)
    monkeypatch.setattr('getpass.getpass', lambda _: password)
    return register()

def mock_login(username, password, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: username)
    monkeypatch.setattr('getpass.getpass', lambda _: password)
    return login()

def mock_create_item(user_id, name, monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: name)
    return create_item(user_id)

# -------------------------------
# Tests
# -------------------------------
def test_register_and_login(db_connection, monkeypatch):
    # Register user
    mock_register("alice", "password123", monkeypatch)
    user_id = mock_login("alice", "password123", monkeypatch)
    assert user_id is not None

def test_create_and_read_item(db_connection, monkeypatch):
    # Register and login
    mock_register("bob", "pass", monkeypatch)
    user_id = mock_login("bob", "pass", monkeypatch)

    # Create an item
    mock_create_item(user_id, "Item1", monkeypatch)

    # Check items in database
    db_connection[0].execute("SELECT name FROM items WHERE owner_id=?", (user_id,))
    items = db_connection[0].fetchall()
    assert items[0][0] == "Item1"

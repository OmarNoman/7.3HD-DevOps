import pytest
import sqlite3
from python_login_webapp.app import app as flask_app, DB_FILE, cursor, conn

# -------------------------------
# Test Setup
# -------------------------------

@pytest.fixture
def test_client():
    # Configure app for testing
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SECRET_KEY'] = 'testkey'
    
    # Use in-memory SQLite database for testing
    test_conn = sqlite3.connect(":memory:", check_same_thread=False)
    test_cursor = test_conn.cursor()
    
    # Create tables in memory
    test_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)
    test_cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        owner_id INTEGER,
        FOREIGN KEY (owner_id) REFERENCES users(id)
    )
    """)
    test_conn.commit()

    # Monkeypatch the app's cursor and connection
    flask_app.config['TEST_CURSOR'] = test_cursor
    flask_app.config['TEST_CONN'] = test_conn

    # Override original cursor in app with test cursor
    global cursor, conn
    old_cursor, old_conn = cursor, conn
    cursor, conn = test_cursor, test_conn

    with flask_app.test_client() as client:
        yield client

    # Restore original cursor and connection
    cursor, conn = old_cursor, old_conn
    test_conn.close()

# -------------------------------
# Test Cases
# -------------------------------

def test_index_page(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Login" in response.data

def test_register_login_logout(test_client):
    # Register
    response = test_client.post("/register", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"login" in response.data.lower()  # redirect to login page

    # Login
    response = test_client.post("/login", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Your Items" in response.data  # dashboard content

    # Logout
    response = test_client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Login" in response.data

def test_create_and_delete_item(test_client):
    # Register and login
    test_client.post("/register", data={"username": "user2", "password": "pass"})
    test_client.post("/login", data={"username": "user2", "password": "pass"})

    # Create item
    response = test_client.post("/create", data={"name": "Item1"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Item1" in response.data

    # Get item id from database
    cursor.execute("SELECT id FROM items WHERE name='Item1'")
    item_id = cursor.fetchone()[0]

    # Delete item
    response = test_client.get(f"/delete/{item_id}", follow_redirects=True)
    assert response.status_code == 200
    assert b"Item1" not in response.data

def test_dashboard_requires_login(test_client):
    # Access dashboard without login
    response = test_client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert b"login" in response.data.lower()

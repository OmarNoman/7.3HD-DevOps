import pytest
from fastapi.testclient import TestClient
from python_login_webapp.app import app
import sqlite3
import os

# -------------------------------
# Setup TestClient
# -------------------------------
client = TestClient(app)

# Use a separate test database
TEST_DB = "test_app.db"

# Override the database connection for testing
def setup_module(module):
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
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
    conn.close()

# -------------------------------
# Helper functions
# -------------------------------
def register_user(username="testuser", password="testpass"):
    return client.post("/register", json={"username": username, "password": password})

def login_user(username="testuser", password="testpass"):
    return client.post("/login", json={"username": username, "password": password})

def create_item(user_id, name="Test Item"):
    return client.post("/items", json={"name": name, "owner_id": user_id})

def read_items(user_id):
    return client.get(f"/items/{user_id}")

def update_item(user_id, item_id, new_name="Updated Item"):
    return client.put(f"/items/{user_id}/{item_id}", json={"name": new_name, "owner_id": user_id})

def delete_item(user_id, item_id):
    return client.delete(f"/items/{user_id}/{item_id}")

# -------------------------------
# Test Cases
# -------------------------------

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "🚀 Python Login & CRUD API is running!"}

def test_register_login_flow():
    # Register a user
    response = register_user()
    assert response.status_code in [200, 400]  # 400 if user already exists

    # Login with correct credentials
    response = login_user()
    assert response.status_code in [200, 401]
    if response.status_code == 200:
        data = response.json()
        assert "user_id" in data
        user_id = data["user_id"]

        # CRUD operations
        # Create an item
        create_resp = create_item(user_id)
        assert create_resp.status_code == 200
        assert create_resp.json()["message"] == "✅ Item successfully created!"

        # Read items
        read_resp = read_items(user_id)
        assert read_resp.status_code == 200
        items = read_resp.json()["items"]
        assert len(items) >= 1
        item_id = items[0]["id"]

        # Update item
        update_resp = update_item(user_id, item_id)
        assert update_resp.status_code == 200
        assert update_resp.json()["message"] == "✅ Item successfully updated!"

        # Delete item
        delete_resp = delete_item(user_id, item_id)
        assert delete_resp.status_code == 200
        assert delete_resp.json()["message"] == "✅ Item successfully deleted!"

def test_invalid_login():
    response = login_user(username="wronguser", password="wrongpass")
    assert response.status_code == 401
    assert response.json()["detail"] == "❌ Incorrect username or password."

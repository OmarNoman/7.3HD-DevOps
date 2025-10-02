import os
import pytest
from python_login_webapp.app import app, init_db

# Use in-memory database for testing
os.environ["DB_FILE"] = ":memory:"

# -------------------------------
# Test client fixture
# -------------------------------
@pytest.fixture(scope="function")
def test_client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    init_db()  # Create tables in memory

    with app.test_client() as client:
        yield client

# -------------------------------
# Tests
# -------------------------------
def test_index_page(test_client):
    rv = test_client.get("/")
    assert rv.status_code == 200
    assert b"Register" in rv.data or b"Login" in rv.data

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

def test_dashboard_requires_login(test_client):
    rv = test_client.get("/dashboard", follow_redirects=True)
    assert b"Login" in rv.data

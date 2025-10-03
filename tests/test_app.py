import os
import sys
import pytest

# Add app folder to path
sys.path.append("./python_login_webapp")

from app import app, setup_db, connect_db

# Use in-memory database for testing
os.environ["DB_FILE"] = ":memory:"


@pytest.fixture(scope="function")
def client():
    """Flask test client with fresh in-memory DB."""
    app.config["TESTING"] = True
    setup_db()  # Recreate tables for each test

    with app.test_client() as c:
        yield c


# ---------------- Tests ----------------
def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Register" in res.data or b"Login" in res.data


def test_register_login_logout(client):
    # Register user
    res = client.post("/register", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert res.status_code == 200

    # Login
    res = client.post("/login", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert b"Your Items" in res.data

    # Logout
    res = client.get("/logout", follow_redirects=True)
    assert res.status_code == 200
    assert b"Register" in res.data or b"Login" in res.data


def test_create_and_delete_item(client):
    # Register & login
    client.post("/register", data={"username": "user2", "password": "pass"})
    client.post("/login", data={"username": "user2", "password": "pass"})

    # Create an item
    res = client.post("/create", data={"name": "Item1"}, follow_redirects=True)
    assert b"Item1" in res.data

    # Grab item id directly from DB
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM items WHERE name=?", ("Item1",))
    item_id = cur.fetchone()["id"]
    conn.close()

    # Delete the item
    res = client.get(f"/delete/{item_id}", follow_redirects=True)
    assert b"Item1" not in res.data


def test_dashboard_requires_login(client):
    res = client.get("/dashboard", follow_redirects=True)
    assert b"Login" in res.data

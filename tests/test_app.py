import os
import sys
import pytest

# Add app folder to path
sys.path.append("./python_login_webapp")

from app import app, setupDatabase, connectDatabase

# Use in-memory database for testing
os.environ["DB_FILE"] = ":memory:"


@pytest.fixture(scope="function")
def testClient():
    """Flask test testClient with fresh in-memory DB."""
    app.config["TESTING"] = True
    setupDatabase()  # Recreate tables for each test

    with app.test_client() as c:
        yield c


# ---------------- Tests ----------------
def test_index_page(testClient):
    response = testClient.get("/")
    assert response.status_code == 200
    assert b"Register" in response.data or b"Login" in response.data


def test_register_login_logout(testClient):
    # Register user
    response = testClient.post("/register", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert response.status_code == 200

    # Login
    response = testClient.post("/login", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert b"Your Items" in response.data

    # Logout
    response = testClient.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Register" in response.data or b"Login" in response.data


def test_create_and_delete_item(testClient):
    # Register & login
    testClient.post("/register", data={"username": "user2", "password": "pass"})
    testClient.post("/login", data={"username": "user2", "password": "pass"})

    # Create an item
    response = testClient.post("/create", data={"name": "Item1"}, follow_redirects=True)
    assert b"Item1" in response.data

    # Grab item id directly from DB
    conn = connectDatabase()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM items WHERE name=?", ("Item1",))
    itemID = cursor.fetchone()["id"]
    conn.close()

    # Delete the item
    response = testClient.get(f"/delete/{itemID}", follow_redirects=True)
    assert b"Item1" not in response.data


def test_dashboard_requires_login(testClient):
    response = testClient.get("/dashboard", follow_redirects=True)
    assert b"Login" in response.data

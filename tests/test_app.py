import os
import sys
import pytest

# Adding app to the folder path
sys.path.append("./python_login_webapp")

from app import app, setupDatabase, connectDatabase

# Making use of in memory database for testing
os.environ["DB_FILE"] = ":memory:"


@pytest.fixture(scope="function")
def testClient():
    """Flask test testClient with fresh in-memory DB."""
    app.config["TESTING"] = True
    setupDatabase()  # Recreates the tables for each test

    with app.test_client() as c:
        yield c


# Tests 
def test_index_page(testClient):
    response = testClient.get("/")
    assert response.status_code == 200
    assert b"Register" in response.data or b"Login" in response.data


def test_register_login_logout(testClient):
    # First registers the user
    response = testClient.post("/register", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert response.status_code == 200

    # Logs in the test user
    response = testClient.post("/login", data={"username": "testuser", "password": "pass"}, follow_redirects=True)
    assert b"Your Items" in response.data

    # Logs out the test user
    response = testClient.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Register" in response.data or b"Login" in response.data


def test_create_and_delete_item(testClient):
    # Registering and logining in the test user
    testClient.post("/register", data={"username": "user2", "password": "pass"})
    testClient.post("/login", data={"username": "user2", "password": "pass"})

    # Creates an item to test
    response = testClient.post("/create", data={"name": "Item1"}, follow_redirects=True)
    assert b"Item1" in response.data

    # Grabs the item id from the database
    conn = connectDatabase()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM items WHERE name=?", ("Item1",))
    itemID = cursor.fetchone()["id"]
    conn.close()

    # Deletes the item from the database
    response = testClient.get(f"/delete/{itemID}", follow_redirects=True)
    assert b"Item1" not in response.data


def test_dashboard_requires_login(testClient):
    response = testClient.get("/dashboard", follow_redirects=True)
    assert b"Login" in response.data

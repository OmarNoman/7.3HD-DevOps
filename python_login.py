import os
import sqlite3
import getpass

# -------------------------------
# Database setup
# -------------------------------
conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# Creating the users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# Create the  items table for CRUD operations
cursor.execute("""
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    owner_id INTEGER,
    FOREIGN KEY (owner_id) REFERENCES users(id)
)
""")
conn.commit()

# -------------------------------
# Authentication functions
# -------------------------------
def register():
    username = os.environ.get("USERNAME") or input("Choose your username: ")
    password = os.environ.get("PASSWORD") or getpass.getpass("Choose a password: ")

    # username = input("Choose your username: ")
    # password = getpass.getpass("Choose a password: ")

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("✅ Registered successfully!")
    except sqlite3.IntegrityError:
        print("⚠️ Username already exists. Try again!")

def login():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()

    if result:
        print("✅ Login successful!")
        return result[0]  # user_id
    else:
        print("❌ Incorrect Username or Password.")
        return None

# -------------------------------
# CRUD functions
# -------------------------------
def create_item(user_id):
    name = input("Enter the item name: ")
    cursor.execute("INSERT INTO items (name, owner_id) VALUES (?, ?)", (name, user_id))
    conn.commit()
    print("✅ Item Successfully created!")

def read_items(user_id):
    cursor.execute("SELECT id, name FROM items WHERE owner_id=?", (user_id,))
    items = cursor.fetchall()
    print("\n📦 Your Items:")
    for item in items:
        print(f"- [{item[0]}] {item[1]}")
    if not items:
        print("⚠️ No items found.")

def update_item(user_id):
    read_items(user_id)
    item_id = input("Enter ID of the item: ")
    new_name = input("Update name: ")
    cursor.execute("UPDATE items SET name=? WHERE id=? AND owner_id=?", (new_name, item_id, user_id))
    conn.commit()
    print("✅ Item Successfully updated!")

def delete_item(user_id):
    read_items(user_id)
    item_id = input("Enter ID of the item to delete: ")
    cursor.execute("DELETE FROM items WHERE id=? AND owner_id=?", (item_id, user_id))
    conn.commit()
    print("✅ Item Successfully deleted!")

# -------------------------------
# Main app loop
# -------------------------------
def main():
    print("=== Simple Login and  CRUD App ===")
    while True:
        choice = input("\n1. Register\n2. Login\n3. Exit\nChoose: ")
        if choice == "1":
            register()
        elif choice == "2":
            user_id = login()
            if user_id:
                while True:
                    action = input("\n1. Create\n2. Read\n3. Update\n4. Delete\n5. Logout\nChoose: ")
                    if action == "1":
                        create_item(user_id)
                    elif action == "2":
                        read_items(user_id)
                    elif action == "3":
                        update_item(user_id)
                    elif action == "4":
                        delete_item(user_id)
                    elif action == "5":
                        print("👋 Logged out.")
                        break
        elif choice == "3":
            print("👋 Goodbye! Thank you!")
            break

if __name__ == "__main__":
    main()

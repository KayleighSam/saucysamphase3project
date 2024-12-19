import sqlite3

DB_PATH = 'fastfood.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Fetch all active menu items
def fetch_menu_items():
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM menu WHERE status = "active"')
    menu_items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return menu_items

# Add a new menu item
def add_menu_item(name, description, price, status, image):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO menu (name, description, price, status, image) VALUES (?, ?, ?, ?, ?)",
        (name, description, price, status, image)
    )

    conn.commit()
    conn.close()

# Update a menu item
def update_menu_item(item_id, name, description, price, status, image):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE menu SET name = ?, description = ?, price = ?, status = ?, image = ? WHERE id = ?",
        (name, description, price, status, image, item_id)
    )

    conn.commit()
    conn.close()

# Delete a menu item
def delete_menu_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM menu WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

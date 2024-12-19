import sqlite3

DB_PATH = 'fastfood.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create 'menu' table with 'quantity' column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL,
        status TEXT,
        image TEXT,
        category TEXT,
        quantity INTEGER DEFAULT 0  -- Add quantity column with default value 0
    )
    ''')

    # Create 'orders' table with 'order_date' column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        status TEXT,
        phone TEXT,
        address TEXT,
        order_number TEXT UNIQUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- Add created_at column
        order_date DATE DEFAULT (DATE('now'))  -- Add order_date column with default to current date
    )
    ''')

    # Create 'order_details' table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        food_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (food_id) REFERENCES menu(id)
    )
    ''')

    # Insert sample records into 'menu' with categories and quantity
    cursor.executemany('''
    INSERT INTO menu (name, description, price, status, image, category, quantity)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', [
        ('Burger', 'A delicious beef burger with cheese', 5.99, 'available', 'https://via.placeholder.com/150', 'Main Course', 100),
        ('Pizza', 'Cheese and tomato pizza', 8.99, 'available', 'https://via.placeholder.com/150', 'Main Course', 50),
        ('Fries', 'Crispy golden fries', 2.99, 'available', 'https://via.placeholder.com/150', 'Sides', 200),
        ('Soda', 'Refreshing cola drink', 1.49, 'available', 'https://via.placeholder.com/150', 'Drinks', 300),
        ('Ice Cream', 'Creamy chocolate ice cream', 3.99, 'available', 'https://via.placeholder.com/150', 'Dessert', 150)
    ])

    # Insert a sample order (for testing purposes)
    cursor.execute('''
    INSERT INTO orders (user_id, status, phone, address, order_number, created_at, order_date) 
    VALUES (?, ?, ?, ?, ?, datetime('now'), DATE('now'))  -- Use current timestamp for created_at and current date for order_date
    ''', (1, 'pending', '123456789', '123 Main St', '1001'))  # Example order number '1001'

    # Get the inserted order ID
    order_id = cursor.lastrowid

    # Insert sample order details (for testing purposes)
    cursor.executemany('''
    INSERT INTO order_details (order_id, food_id, quantity)
    VALUES (?, ?, ?)
    ''', [
        (order_id, 1, 2),  # 2 Burgers
        (order_id, 2, 1),  # 1 Pizza
        (order_id, 3, 1)   # 1 Fries
    ])

    conn.commit()
    conn.close()
    print("Database, tables, and sample records created successfully!")

if __name__ == '__main__':
    init_db()

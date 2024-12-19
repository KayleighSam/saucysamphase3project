from flask import Flask, render_template, request, session, redirect, url_for
import sqlite3
import os
import random
import time

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'app/templates'))
app.secret_key = 'your_secret_key'  # To secure the session
DB_PATH = 'fastfood.db'

# Function to generate a unique order number
def generate_order_number():
    timestamp = int(time.time())  # Current time in seconds since epoch
    random_number = random.randint(1000, 9999)  # Random number to ensure uniqueness
    return f"{timestamp}-{random_number}"

# Route to fetch menu items by category
@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all unique categories from the menu
    cursor.execute("SELECT DISTINCT category FROM menu WHERE status = 'available'")
    categories = cursor.fetchall()

    # Fetch all available menu items
    cursor.execute("SELECT * FROM menu WHERE status = 'available'")
    menu_items = cursor.fetchall()

    conn.close()

    # Get cart items from session
    cart_items = session.get('cart', [])

    return render_template('menu.html', menu_items=menu_items, categories=categories, cart_items=cart_items)

# Route to fetch menu items by category
@app.route('/category/<category_name>')
def category(category_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all unique categories from the menu
    cursor.execute("SELECT DISTINCT category FROM menu WHERE status = 'available'")
    categories = cursor.fetchall()

    # Fetch menu items for the selected category
    cursor.execute("SELECT * FROM menu WHERE category = ? AND status = 'available'", (category_name,))
    menu_items = cursor.fetchall()

    conn.close()

    # Get cart items from session
    cart_items = session.get('cart', [])

    return render_template('menu.html', menu_items=menu_items, categories=categories, category_name=category_name, cart_items=cart_items)

# Route to list all items
@app.route('/all_items')
def all_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch all menu items
    cursor.execute("SELECT * FROM menu WHERE status = 'available'")
    menu_items = cursor.fetchall()

    conn.close()

    # Get cart items from session
    cart_items = session.get('cart', [])

    return render_template('menu.html', menu_items=menu_items, cart_items=cart_items)

# Route to view a specific item detail
@app.route('/item_detail/<int:item_id>')
def item_detail(item_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch item details
    cursor.execute("SELECT * FROM menu WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    conn.close()

    return render_template('item_detail.html', item=item)

# Route to add item to the shopping cart
@app.route('/add_to_cart/<int:item_id>')
def add_to_cart(item_id):
    cart = session.get('cart', [])

    # Check if the item already exists in the cart
    cart.append(item_id)

    # Save the updated cart back into the session
    session['cart'] = cart

    return redirect(url_for('index'))

# Route to remove an item from the cart
@app.route('/remove_from_cart/<int:item_id>')
def remove_from_cart(item_id):
    cart = session.get('cart', [])

    # Remove item from the cart
    if item_id in cart:
        cart.remove(item_id)

    # Save the updated cart back into the session
    session['cart'] = cart

    return redirect(url_for('view_cart'))

# Route to increase the quantity of an item in the cart
@app.route('/increase_quantity/<int:item_id>')
def increase_quantity(item_id):
    cart = session.get('cart', [])

    # Add the item again to the cart (this increases the quantity)
    cart.append(item_id)

    # Save the updated cart back into the session
    session['cart'] = cart

    return redirect(url_for('view_cart'))

# Route to decrease the quantity of an item in the cart
@app.route('/decrease_quantity/<int:item_id>')
def decrease_quantity(item_id):
    cart = session.get('cart', [])

    # Remove one occurrence of the item (this decreases the quantity)
    if item_id in cart:
        cart.remove(item_id)

    # Save the updated cart back into the session
    session['cart'] = cart

    return redirect(url_for('view_cart'))

# Route to view the cart
@app.route('/view_cart')
def view_cart():
    cart = session.get('cart', [])
    
    # If cart is empty, redirect back to the menu page
    if not cart:
        return redirect(url_for('index'))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch the items in the cart from the menu
    cursor.execute("SELECT * FROM menu WHERE id IN ({})".format(','.join(['?']*len(cart))), cart)
    items = cursor.fetchall()

    # Calculate the total amount
    total_amount = 0
    for item in items:
        total_amount += item[3] * cart.count(item[0])

    conn.close()

    return render_template('cart.html', items=items, cart_items=cart, total_amount=total_amount)

# Route to checkout and insert the order into the database
@app.route('/checkout', methods=['POST'])
def checkout():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get cart items from session
    cart_items = session.get('cart', [])
    phone = request.form.get('phone')  # Get the phone number from the form

    if not cart_items:
        return redirect(url_for('view_cart'))

    # Generate the order number
    order_number = generate_order_number()

    # Insert the order into the orders table with the generated order number
    cursor.execute("INSERT INTO orders (user_id, status, phone, address, order_number) VALUES (?, ?, ?, ?, ?)", 
                   (1, 'pending', phone, request.form.get('address'), order_number))  # Pass order_number as string
    order_id = cursor.lastrowid

    # Insert the order details
    for item_id in cart_items:
        cursor.execute("INSERT INTO order_details (order_id, food_id, quantity) VALUES (?, ?, ?)",
                       (order_id, item_id, cart_items.count(item_id)))

    # Commit the transaction and clear the cart
    conn.commit()
    session['cart'] = []  # Clear the cart after checkout

    conn.close()

    # Save order_id in the session to track orders
    session['last_order_id'] = order_id

    return redirect(url_for('order_confirmation', order_id=order_id))  # Ensure order_id is passed

# Route to show order confirmation
@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch order details
    cursor.execute('''
        SELECT menu.name, menu.price, order_details.quantity
        FROM order_details
        JOIN menu ON order_details.food_id = menu.id
        WHERE order_details.order_id = ?
    ''', (order_id,))
    order_details = cursor.fetchall()

    cursor.execute("SELECT SUM(menu.price * order_details.quantity) FROM order_details JOIN menu ON order_details.food_id = menu.id WHERE order_details.order_id = ?", (order_id,))
    total_amount = cursor.fetchone()[0]

    conn.close()

    return render_template('order_confirmation.html', order_details=order_details, total_amount=total_amount, order_number=order_id)

# Route to track an order by order_id
@app.route('/track_order/<int:order_id>')
def track_order(order_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch order details based on order_id
    cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    order = cursor.fetchone()

    # Fetch items in the order (assuming you have an order_details table linking orders and menu items)
    cursor.execute('''
        SELECT menu.name, menu.price, order_details.quantity
        FROM order_details
        JOIN menu ON order_details.food_id = menu.id
        WHERE order_details.order_id = ?
    ''', (order_id,))
    order_items = cursor.fetchall()

    conn.close()

    if order:
        return render_template('track_order.html', order=order, order_items=order_items)
    else:
        return "Order not found", 404

# Route to show user's past orders
@app.route('/my_orders', methods=['GET', 'POST'])
def my_orders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Get the selected order date from the form
        order_date = request.form.get('order_date')

        # Query the orders for the specific date
        cursor.execute("SELECT * FROM orders WHERE user_id = 1 AND date(created_at) = ?", (order_date,))
    else:
        # Default query to get all orders if no date is selected
        cursor.execute("SELECT * FROM orders WHERE user_id = 1")  # Adjust user_id as needed

    orders = cursor.fetchall()

    conn.close()

    return render_template('my_orders.html', orders=orders)

# Include routes related to admin functionality from the admin module
from admin import admin_bp

# Register the admin blueprint
app.register_blueprint(admin_bp, url_prefix='/admin')

if __name__ == '__main__':
    app.run(debug=True)

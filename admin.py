from flask import Blueprint, render_template, request, redirect, url_for, flash
import sqlite3

# Define the admin blueprint
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

# Admin Dashboard Route
@admin_bp.route('/')
def admin_dashboard():
    conn = sqlite3.connect('fastfood.db')
    cursor = conn.cursor()

    # Fetch counts of orders based on status
    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'")
    pending_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Confirmed'")
    confirmed_orders = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'Canceled'")
    canceled_orders = cursor.fetchone()[0]

    conn.close()

    # Render the admin dashboard with order counts
    return render_template(
        'admin_dashboard.html',
        pending_orders=pending_orders,
        confirmed_orders=confirmed_orders,
        canceled_orders=canceled_orders
    )




# Admin Orders Route
@admin_bp.route('/orders', methods=['GET'])
def admin_orders():
    search_query = request.args.get('search', '')

    conn = sqlite3.connect('fastfood.db')
    cursor = conn.cursor()

    # Search functionality: match Order ID, User ID, or Status
    if search_query:
        cursor.execute("""
            SELECT * FROM orders
            WHERE id LIKE ? OR user_id LIKE ? OR status LIKE ?
        """, ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
    else:
        cursor.execute("SELECT * FROM orders")

    orders = cursor.fetchall()
    conn.close()

    # Render the orders page
    return render_template('admin_orders.html', orders=orders, search_query=search_query)

# Admin Order Status Update Route
@admin_bp.route('/update_order_status/<int:order_id>', methods=['POST'])
def update_order_status(order_id):
    new_status = request.form.get('status')

    conn = sqlite3.connect('fastfood.db')
    cursor = conn.cursor()

    # Update the order status in the database
    cursor.execute('''
        UPDATE orders
        SET status = ?
        WHERE id = ?
    ''', (new_status, order_id))

    conn.commit()
    conn.close()

    flash('Order status updated successfully!', 'success')
    return redirect(url_for('admin.admin_orders'))

# Admin Menu Route
@admin_bp.route('/menu')
def admin_menu():
    conn = sqlite3.connect('fastfood.db')
    cursor = conn.cursor()

    # Fetch all menu items from the database
    cursor.execute("SELECT * FROM menu")
    menu_items = cursor.fetchall()

    conn.close()

    # Render the menu management page
    return render_template('admin_menu.html', menu_items=menu_items)

# Edit Menu Item Route
@admin_bp.route('/edit_item/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    conn = sqlite3.connect('fastfood.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Handle the form submission for editing a menu item
        name = request.form.get('name')
        price = request.form.get('price')
        category = request.form.get('category')
        status = request.form.get('status')

        # Update the item in the menu
        cursor.execute('''
            UPDATE menu
            SET name = ?, price = ?, category = ?, status = ?
            WHERE id = ?
        ''', (name, price, category, status, item_id))

        conn.commit()
        conn.close()

        flash('Menu item updated successfully!', 'success')
        return redirect(url_for('admin.admin_menu'))

    # Fetch the existing item details for the form (GET request)
    cursor.execute("SELECT * FROM menu WHERE id = ?", (item_id,))
    item = cursor.fetchone()

    conn.close()

    # Render the edit item form
    return render_template('edit_item.html', item=item)

# Add New Menu Item Route
@admin_bp.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        # Handle form submission for adding a new menu item
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        category = request.form.get('category')
        status = request.form.get('status')
        image = request.form.get('image')  # image URL field

        conn = sqlite3.connect('fastfood.db')
        cursor = conn.cursor()

        # Insert the new item into the menu
        cursor.execute('''
            INSERT INTO menu (name, description, price, status, image, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, price, status, image, category))

        conn.commit()
        conn.close()

        flash('New menu item added successfully!', 'success')
        return redirect(url_for('admin.admin_menu'))

    # Render the add item form
    return render_template('add_item.html')

# Delete Menu Item Route
@admin_bp.route('/delete_item/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = sqlite3.connect('fastfood.db')
    cursor = conn.cursor()

    # Delete the item from the menu
    cursor.execute("DELETE FROM menu WHERE id = ?", (item_id,))

    conn.commit()
    conn.close()

    flash('Menu item deleted successfully!', 'success')
    return redirect(url_for('admin.admin_menu'))

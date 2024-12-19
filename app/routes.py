from flask import Blueprint, render_template, request, redirect, url_for
from .models import fetch_menu_items, add_menu_item, update_menu_item, delete_menu_item

main_blueprint = Blueprint('main', __name__)

# Landing Page (Home)
@main_blueprint.route('/')
def index():
    return render_template('index.html')

# Menu Page
@main_blueprint.route('/menu')
def menu():
    menu_items = fetch_menu_items()
    return render_template('menu.html', menu_items=menu_items)

# Admin Dashboard
@main_blueprint.route('/admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Add a new menu item (Admin)
@main_blueprint.route('/admin/add_menu_item', methods=['POST'])
def add_menu():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    status = request.form['status']
    image = request.form['image']
    
    add_menu_item(name, description, price, status, image)
    return redirect(url_for('main.admin_dashboard'))

# Edit an existing menu item (Admin)
@main_blueprint.route('/admin/edit_menu_item/<int:item_id>', methods=['GET', 'POST'])
def edit_menu_item(item_id):
    conn = get_db_connection()
    cursor = conn.execute('SELECT * FROM menu WHERE id = ?', (item_id,))
    item = cursor.fetchone()
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        status = request.form['status']
        image = request.form['image']
        
        update_menu_item(item_id, name, description, price, status, image)
        return redirect(url_for('main.admin_dashboard'))

    return render_template('edit_menu_item.html', item=item)

# Delete a menu item (Admin)
@main_blueprint.route('/admin/delete_menu_item/<int:item_id>', methods=['GET'])
def delete_menu_item_route(item_id):
    delete_menu_item(item_id)
    return redirect(url_for('main.admin_dashboard'))

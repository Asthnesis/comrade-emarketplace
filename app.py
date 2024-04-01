# comrade-emarketplace
from flask import flash
import logging
import pymysql.cursors
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, url_for, request, redirect, session, jsonify, flash
from authlib.integrations.flask_client import OAuth
import pymysql
import base64
import requests
from requests.auth import HTTPBasicAuth
import uuid
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.secret_key = ("84hrfnsdlkamk93")


connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',
                             database='comrade',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

consumer_key = 'PKreMGJ7wTszUSnPOnZJcdPQEUbBcNDcCYu9IOqvqdYHrIbr'
consumer_secret = '3UOS9ruBBQqK5qJrSxSKdos8JzdMXU1kAZEuUOUuDByn2LBXeODVyNqJGUVRXJT0'


@app.route('/initiate_payment')
def initiate_payment():
    # partyA = '254729854464'
    partyA = '254741889010'
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

    try:
        access_token = get_access_token()
        if access_token:
            headers = {'Authorization': 'Bearer %s' % access_token}
            timestamp = datetime.now()
            times = timestamp.strftime("%Y%m%d%H%M%S")
            password = '174379' + \
                'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919' + times
            password = base64.b64encode(password.encode('utf-8'))
            password = password.decode('utf-8')
            payload = {
                "BusinessShortCode": "174379",
                "Password": password,
                "Timestamp": times,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": "1",
                "PartyA": partyA,
                "PartyB": "174379",
                "PhoneNumber": partyA,
                "CallBackURL": "https://a13f-197-237-160-31.ngrok-free.app/callback",
                "AccountReference": "Test",
                "TransactionDesc": "Test Payment",
            }

            response = requests.post(endpoint, json=payload, headers=headers)

            return 'Success, Request accepted for processing'
        else:
            return 'Access token not found'
    except requests.RequestException as e:
        return f'Error: {e}'


@app.route('/stk_callback', methods=["POST", 'GET'])
def stk_callback():
    data = request.get_json()
    print(data)
    return 'ok'


def get_access_token():
    consumer_key = 'PKreMGJ7wTszUSnPOnZJcdPQEUbBcNDcCYu9IOqvqdYHrIbr'
    consumer_secret = '3UOS9ruBBQqK5qJrSxSKdos8JzdMXU1kAZEuUOUuDByn2LBXeODVyNqJGUVRXJT0'
    mpesa_auth_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    try:
        data = requests.get(mpesa_auth_url, auth=HTTPBasicAuth(
            consumer_key, consumer_secret))
        data.raise_for_status()
        dict_data = data.json()
        return dict_data.get('access_token')
    except requests.RequestException as e:
        print(f'Error: {e}')
        return None


@app.route('/')
def index():
    try:
        with connection.cursor() as cursor:
            sql = "SELECT p.*, pi.product_image FROM product p LEFT JOIN product_images pi ON p.product_id = pi.product_id"
            cursor.execute(sql)
            products = cursor.fetchall()
            cart_count = session.get('cart_count', 0)
            for product in products:
                if product['product_image'] is not None:
                    product['product_image'] = base64.b64encode(
                        product['product_image']).decode('utf-8')
            return render_template('index.html', products=products, cart_count=cart_count)
    except pymysql.Error as e:
        print("Error fetching product from database", e)
        flash("An error occurred while fetching products.")
        return redirect(url_for('index'))


@app.route('/filter/<category>')
def filter_products(category):
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT p.*, pi.product_image 
                FROM product p 
                LEFT JOIN product_images pi ON p.product_id = pi.product_id
                WHERE p.category = %s
            """
            cursor.execute(sql, (category,))
            products = cursor.fetchall()
            cart_count = session.get('cart_count', 0)
            for product in products:
                if product['product_image'] is not None:
                    product['product_image'] = base64.b64encode(
                        product['product_image']).decode('utf-8')
            if not products:
                flash("No products found in this category.")
            return render_template('index.html', products=products, cart_count=cart_count)
    except pymysql.Error as e:
        print("Error fetching product from database", e)
        flash("An error occurred while fetching products.")
        return redirect(url_for('index'))


@app.route('/search', methods=['POST'])
def search_products():
    try:
        search_query = request.form.get('search_query').strip().lower()

        with connection.cursor() as cursor:
            sql = """
                SELECT p.*, pi.product_image 
                FROM product p 
                LEFT JOIN product_images pi ON p.product_id = pi.product_id
                WHERE LOWER(p.prod_name) LIKE %s
            """
            cursor.execute(sql, ('%' + search_query + '%',))
            products = cursor.fetchall()
            cart_count = session.get('cart_count', 0)
            for product in products:
                if product['product_image'] is not None:
                    product['product_image'] = base64.b64encode(
                        product['product_image']).decode('utf-8')
            if not products:
                flash("No products found matching your search.")
            return render_template('index.html', products=products, cart_count=cart_count)
    except pymysql.Error as e:
        print("Error fetching product from database", e)
        flash("An error occurred while fetching products.")
        return redirect(url_for('index'))


@app.route('/product_card/<string:product_id>', methods=['GET'])
def product_card(product_id):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT p.*, pi.product_image FROM product p LEFT JOIN product_images pi ON p.product_id = pi.product_id WHERE p.product_id = %s"
            cursor.execute(sql, (product_id,))
            product = cursor.fetchone()
            cart_count = session.get('cart_count', 0)
            if product:
                if product['product_image'] is not None:
                    product['product_image'] = base64.b64encode(
                        product['product_image']).decode('utf-8')
                return render_template('product_card.html', product=product, cart_count=cart_count)
            else:
                return "Product not found", 404
    except pymysql.Error as e:
        print("Error fetching product from database", e)
        return "An error occurred while fetching the product", 500


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/seller_register')
def seller_register():
    return render_template('seller_register.html')


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/seller_login')
def seller_login():
    return render_template("seller_login.html")


@app.route('/checkout')
def checkout():
    try:
        user_id = session['user_id']
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM user_account WHERE user_id = %s", (user_id,))
            user_details = cursor.fetchone()
            cursor.execute(
                "SELECT * FROM cart WHERE user_id = %s", (user_id,))
            cart_details = cursor.fetchone()

            return render_template('checkout.html', user_details=user_details, cart_details=cart_details)

    except pymysql.err.InterfaceError as e:
        flash(f"Error connecting to database: {e}")
        return "An error occurred while fetching user details"


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        if 'role' in session and session['role'] == 'seller':
            flash("Please log in as a seller.")
            return redirect(url_for('seller_login'))
        else:
            flash("Please log in.")
            return redirect(url_for('login'))

    try:
        user_id = session['user_id']
        with connection.cursor() as cursor:
            sql = "SELECT u.*, b.buyer_id, s.seller_id FROM user_account u LEFT JOIN buyer b ON u.user_id = b.user_id LEFT JOIN seller s ON u.user_id = s.user_id WHERE u.user_id = %s"
            cursor.execute(sql, (user_id,))
            user_data = cursor.fetchone()

        if user_data:
            first_name = user_data['first_name']
            last_name = user_data['last_name']
            email = user_data['email']
            buyer_id = user_data['buyer_id']
            seller_id = user_data['seller_id']
            cart_count = session.get('cart_count', 0)

            return render_template('profile.html', user_id=user_id, first_name=first_name, last_name=last_name, email=email, buyer_id=buyer_id, seller_id=seller_id, cart_count=cart_count)
        else:
            flash("User data not found.")
            return "User data not found"

    except pymysql.err.InterfaceError as e:
        flash(f"Error connecting to database: {e}")
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('fname', None)
    session.pop('lname', None)
    session.pop('role', None)

    return redirect(url_for('index'))


@app.route('/cart')
def cart():
    if 'user_id' not in session:
        print('You need to be logged in to view your cart', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']

    try:
        with connection.cursor() as cursor:
            # Fetch cart items
            cart_sql = """SELECT * FROM cart WHERE user_id = %s"""
            cursor.execute(cart_sql, (user_id,))
            cart_items = cursor.fetchall()

            if cart_items:
                product_ids = [item['product_id'] for item in cart_items]

                # Fetch product details for cart items
                product_sql = """SELECT p.*, pi.product_image 
                                 FROM product p 
                                 INNER JOIN product_images pi ON p.product_id = pi.product_id 
                                 WHERE p.product_id IN ({})""".format(','.join(['%s']*len(product_ids)))
                cursor.execute(product_sql, product_ids)
                products = cursor.fetchall()

                # Convert images to base64
                for product in products:
                    product['product_image'] = base64.b64encode(
                        product['product_image']).decode('utf-8')

                # Combine cart items with product details
                for cart_item in cart_items:
                    for product in products:
                        if cart_item['product_id'] == product['product_id']:
                            cart_item.update(product)
                            break

            cart_count = session.get('cart_count', 0)
            total_price = sum(item['price'] * item['quantity']
                              for item in cart_items)

            return render_template('cart.html', cart_items=cart_items, cart_count=cart_count, total_price=total_price)
    except Exception as e:
        return 'Error fetching cart items: {}'.format(str(e)), 'error'


@app.route('/add_to_favourites', methods=['POST'])
def add_to_favourites():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_id = session['user_id']
    product_id = request.json.get('product_id')

    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID not provided'})

    try:
        with connection.cursor() as cursor:
            # Check if the product is already in the favorites
            sql = "SELECT COUNT(*) AS count FROM favourites WHERE user_id = %s AND product_id = %s"
            cursor.execute(sql, (user_id, product_id))
            result = cursor.fetchone()

            if result['count'] > 0:
                return jsonify({'success': False, 'message': 'Product already in favorites'})

            # Add the product to the favorites
            sql = "INSERT INTO favourites (user_id, product_id) VALUES (%s, %s)"
            cursor.execute(sql, (user_id, product_id))
            connection.commit()

            return jsonify({'success': True, 'message': 'Product added to favorites successfully'})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': 'An error occurred while processing the request'}), 500


@app.route('/seller_dashboard', methods=['GET', 'POST'])
def seller_dashboard():
    if 'seller_id' not in session:
        return redirect(url_for('seller_login'))

    if request.method == 'GET':
        try:
            user_id = session['user_id']
            with connection.cursor() as cursor:
                sql = "SELECT u.*, b.buyer_id, s.seller_id FROM user_account u LEFT JOIN buyer b ON u.user_id = b.user_id LEFT JOIN seller s ON u.user_id = s.user_id WHERE u.user_id = %s"
                cursor.execute(sql, (user_id,))
                user_data = cursor.fetchone()

            if user_data:
                first_name = user_data['first_name']
                last_name = user_data['last_name']
                email = user_data['email']
                buyer_id = user_data['buyer_id']
                seller_id = user_data['seller_id']
                cart_count = session.get('cart_count', 0)
                seller_id = session['seller_id']
                products = fetch_product_data_from_database(seller_id)
                for product in products:
                    if product['product_image'] is not None:
                        product['product_image'] = base64.b64encode(
                            product['product_image']).decode('utf-8')
                return render_template('seller_dashboard.html', products=products, user_id=user_id, first_name=first_name, last_name=last_name, email=email, buyer_id=buyer_id, seller_id=seller_id, cart_count=cart_count)

            else:
                flash("User data not found.")
                return "User data not found"

        except pymysql.err.InterfaceError as e:
            flash(f"Error connecting to database: {e}")
            return redirect(url_for('login'))

    elif request.method == 'POST':
        if request.form.get('action') == 'delete':
            product_id = request.form.get('product_id')
            delete_product_from_database(product_id)
        elif request.form.get('action') == 'edit':
            # Add logic for editing products here
            pass

        return redirect(url_for('seller_dashboard'))


@app.route('/favourites')
def favourites():
    return render_template('favourites.html')


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'User not logged in'})

    user_id = session['user_id']
    product_id = request.json.get('product_id')

    if not product_id:
        return jsonify({'success': False, 'message': 'Product ID not provided'})

    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM product WHERE product_id = %s"
            cursor.execute(sql, (product_id,))
            product = cursor.fetchone()
            price = product['price']

            if not product:
                return jsonify({'success': False, 'message': 'Product not found'}), 404

            quantity_limit = product['available_units']

            sql = "SELECT quantity FROM cart WHERE user_id = %s AND product_id = %s"
            cursor.execute(sql, (user_id, product_id))
            existing_cart_item = cursor.fetchone()

            current_quantity = existing_cart_item['quantity'] if existing_cart_item else 0

            if current_quantity >= quantity_limit:
                return jsonify({'success': False, 'message': 'Quantity limit reached for this product'})

            if existing_cart_item:
                # If the product is already in the cart, update the quantity
                sql = "UPDATE cart SET quantity = quantity + 1,total_price = total_price + %s WHERE user_id = %s AND product_id = %s"
                cursor.execute(sql, (price, user_id, product_id))
            else:
                sql = "INSERT INTO cart (user_id, product_id, quantity, total_price) VALUES (%s, %s, 1, %s)"
                cursor.execute(sql, (user_id, product_id, price))

            connection.commit()
            update_cart_count()

            return jsonify({'success': True, 'message': 'Product added to cart successfully'})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False, 'message': 'An error occurred while processing the request'}), 500


def update_cart_count():
    try:
        user_id = session.get('user_id')
        if user_id:
            with connection.cursor() as cursor:
                sql = "SELECT SUM(quantity) AS cart_count FROM cart WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                if result:
                    session['cart_count'] = result['cart_count']
                    print("Cart count updated:", result['cart_count'])
                    return result['cart_count']
                else:
                    session['cart_count'] = 0
                    print("Cart count updated:", 0)
                    return 0
        else:
            session['cart_count'] = 0
            print("Cart count updated:", 0)
            return 0
    except Exception as e:
        print("Error updating cart count:", e)
        return 0


def generate_product_id():
    return str(uuid.uuid4())[:8].upper()


def get_sub_category_id(sub_category_name):
    sub_category_mapping = {
        'fiction': 1,
        'non-fiction': 2,
        'mystery': 3,
        'romance': 4,
        'computers': 5,
        'smartphones': 6,
        'televisions': 7,
        'cameras': 8,
        'living-room-furniture': 9,
        'bedroom-furniture': 10,
        'dining-room': 11,
        'office': 12,
        'cleaning': 13,
        'repair': 14,
        'maintenance': 15,
        'consultation': 16,
        'skincare': 17,
        'makeup': 18,
        'haircare': 19,
        'fragrances': 20,
        'stationery': 21,
        'home-decor': 22,
        'kitchenware': 23,
        'sports': 24,
        'travel': 25,
        'entertainment': 26,
    }

    return sub_category_mapping.get(sub_category_name.lower(), None)


def insert_product(product_name, condition, sub_category_name, description, available_units, price, image_data, seller_id):
    try:
        with connection.cursor() as cursor:
            sub_category_id = get_sub_category_id(sub_category_name)
            if sub_category_id:
                product_id = generate_product_id()
                escaped_description = description.replace('\'', '\\\'')
                sql = "INSERT INTO product (product_id, prod_name, prod_condition, sub_cat_id, description, available_units, price, seller_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(
                    sql, (product_id, product_name, condition,
                          sub_category_id, escaped_description, available_units, price, seller_id))
                connection.commit()

                sql = "INSERT INTO product_images (product_id, product_image) VALUES (%s, %s)"
                cursor.execute(sql, (product_id, image_data))
                connection.commit()
                return True
    except Exception as e:
        print("Error inserting product:", e)
        return False


@app.route('/seller_dashboard/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            product_name = request.form['product-name']
            category = request.form['category']
            sub_category_name = request.form['sub-category']
            seller_id = session.get('seller_id')

            files = request.files.getlist('product-images[]')
            for file in files:

                if file.filename != '':
                    filename = secure_filename(file.filename)
                    image_data = file.read()

            price = float(request.form['price'])
            description = request.form['description']
            condition = request.form['condition']
            available_units = int(request.form['units'])

            if insert_product(product_name, condition, sub_category_name, description, available_units, price, image_data, seller_id):
                return redirect(url_for('seller_dashboard'))
            else:
                print('Error inserting product. Please try again.', 'error')
                return redirect(url_for('seller_dashboard'))
        except Exception as e:
            print(f'An error occurred: {str(e)}', 'error')
            return redirect(url_for('seller_dashboard'))
    else:
        return 'Method not allowed'


def fetch_product_data_from_database(seller_id):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT p.*, pi.product_image FROM product p LEFT JOIN product_images pi ON p.product_id = pi.product_id WHERE p.seller_id = %s"
            cursor.execute(sql, (seller_id,))
            products = cursor.fetchall()
        return products
    except pymysql.Error as e:
        print("Error fetching product from database", e)
        return []


def delete_product_from_database(product_id):
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM product WHERE product_id = %s"
            cursor.execute(sql, (product_id,))
            connection.commit()
    except pymysql.Error as e:
        print("Error deleting product from the database:", e)
        flash("An error occurred while deleting the product. Please try again.", "error")
    finally:
        connection.close()
    return redirect(url_for('manage_products'))


# Google O-auth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="32079113759-868616kq5dqlob3dl4i75vh3kqb9cfen.apps.googleusercontent.com",
    client_secret="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",
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    endpoint_url='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid profile email'},
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
)


@app.route('/callback')
def callback():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()

    if 'email' in user_info:
        email = user_info['email']
        role = 'buyer'
        with connection.cursor() as cursor:
            sql = "SELECT u.*, b.buyer_id, s.seller_id FROM user_account u LEFT JOIN buyer b ON u.user_id = b.user_id LEFT JOIN seller s ON u.user_id = s.user_id WHERE u.email = %s"
            try:
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user['user_id']
                    session['email'] = user['email']
                    session['fname'] = user['first_name']
                    session['lname'] = user['last_name']
                    session['role'] = user['role']
                    session['buyer_id'] = user['buyer_id']
                    flash('Login Success!')
                    return redirect(url_for('profile'))
                else:
                    return redirect(url_for('register'))
            except pymysql.Error as e:
                print("Error executing SQL query:", e)
    else:
        return "User information incomplete"

# Register using google O-auth


@app.route('/register_callback')
def register_callback():
    google = oauth.create_client('google')
    redirect_uri = url_for('register_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/register_authorize')
def register_authorize():
    try:
        google = oauth.create_client('google')
        token = google.authorize_access_token()
        resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
        user_info = resp.json()

        if 'email' in user_info:
            email = user_info['email']
            fname = user_info.get('given_name', '')
            lname = user_info.get('family_name', '')

            with connection.cursor() as cursor:
                # Check if the user already exists
                sql = "SELECT * FROM user_account WHERE email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()

                if not user or user['role'] == 'seller':
                    # User doesn't exist, register
                    user_id = user['user_id']
                    buyer_id = generate_seller_id("buyer")
                    role = 'buyer'
                    cursor.execute('''
                        INSERT INTO user (user_id) 
                        VALUES (%s)
                    ''', (user_id,))
                    cursor.execute('''
                        INSERT INTO user_account (user_id, email, first_name, last_name, role) 
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (user_id, email, fname, lname, role))
                    connection.commit()

                    # Insert buyer details into buyer table
                    cursor.execute('''
                        INSERT INTO buyer (user_id, buyer_id) 
                        VALUES (%s, %s)
                    ''', (user_id, buyer_id,))
                    connection.commit()

                    session['user_id'] = user_id
                    session['email'] = email
                    session['fname'] = fname
                    session['lname'] = lname
                    session['role'] = role

                    return redirect(url_for('profile'))
                else:
                    print("User already exists. Please log in ")
                    return redirect(url_for('login'))
    except Exception as e:
        print("Error:", e)
        flash("An error occurred during authorization. Please try again.")
        return redirect(url_for('login'))
# Function to generate unique IDs


def generate_user_id(table):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count_result = cursor.fetchone()
            count = count_result['COUNT(*)'] + 1 if count_result else 1
            return f'{table[0].upper()}{str(count).zfill(3)}'
    except Exception as e:
        print("Error executing query:", e)
        return None

# Function to generate unique buyer IDs


def generate_buyer_id(table):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count_result = cursor.fetchone()
            count = count_result['COUNT(*)'] + \
                1 if count_result and 'COUNT(*)' in count_result else 1
            return f'{table[0].upper()}{str(count).zfill(3)}'
    except Exception as e:
        print("Error executing query:", e)
        return None

# Function to generate unique seller IDs


def generate_seller_id(table):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count_result = cursor.fetchone()
            count = count_result['COUNT(*)'] + 1 if count_result else 1
            return f'{table[0].upper()}{str(count).zfill(3)}'
    except Exception as e:
        print("Error executing query:", e)
        return None


@app.route('/seller_callback')
def seller_callback():
    google = oauth.create_client('google')
    redirect_uri = url_for('seller_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/seller_authorize')
def seller_authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()

    if 'email' in user_info:
        email = user_info['email']
        role = 'seller'
        with connection.cursor() as cursor:
            sql = "SELECT u.*, b.buyer_id, s.seller_id FROM user_account u LEFT JOIN buyer b ON u.user_id = b.user_id LEFT JOIN seller s ON u.user_id = s.user_id WHERE u.email = %s"
            try:
                cursor.execute(sql, (email,))
                user = cursor.fetchone()
                if user:
                    # Process user data
                    print("User found:", user)
                else:
                    print("User not found for email:", email)
            except pymysql.Error as e:
                print("Error executing SQL query:", e)
        if user:
            session['user_id'] = user['user_id']
            session['email'] = user['email']
            session['fname'] = user['first_name']
            session['lname'] = user['last_name']
            session['role'] = user['role']
            session['seller_id'] = user['seller_id']
            return redirect(url_for('seller_dashboard'))
        else:
            return redirect(url_for('seller_register'))
    else:
        return "User information incomplete"

# Register using google O-auth


@app.route('/seller_register_callback')
def seller_register_callback():
    google = oauth.create_client('google')
    redirect_uri = url_for('seller_register_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/seller_register_authorize')
def seller_register_authorize():
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()
    # Generate unique user ID and buyer ID
    user_id = generate_user_id("user")
    seller_id = generate_seller_id("seller")

    if not user or user['role'] == 'buyer':
        email = user_info['email']
        fname = user_info.get('given_name', '')
        lname = user_info.get('family_name', '')

        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM user_account WHERE email = %s"
                cursor.execute(sql, (email,))
                user = cursor.fetchone()

                if not user:
                    # User doesn't exist, store user info in the database
                    # Insert user details into user table
                    role = 'seller'
                    cursor.execute('''
                    INSERT INTO user (user_id) 
                        VALUES (%s)
                    ''', (user_id,))
                    cursor.execute('''
                    INSERT INTO user_account (user_id, email, first_name, last_name, role) 
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (user_id, email, fname, lname, role))
                    connection.commit()
                    flash("Registration successful. Welcome, " + fname + "!")
                else:
                    flash("User already exists. Please log in.")
                    return redirect(url_for('seller_login'))

                if user_id and seller_id:
                    try:
                        # Insert seller details into seller table
                        cursor.execute('''
                            INSERT INTO seller (user_id,seller_id) 
                            VALUES (%s, %s)
                        ''', (user_id, seller_id,))
                        connection.commit()

                        session['user_id'] = user_id
                        session['email'] = email
                        session['fname'] = fname
                        session['lname'] = lname
                        session['role'] = role

                        return redirect(url_for('seller_dashboard'))
                    except Exception as e:
                        print("Error:", e)
                        flash(
                            "An error occurred during registration. Please try again.")
                        return redirect(url_for('seller_login'))

                else:
                    return "Error: Unable to generate IDs"

        except pymysql.err.InterfaceError as e:
            print("Error connecting to database:", e)
            flash("An error occurred during registration. Please try again.")
            return redirect(url_for('seller_login'))
        except pymysql.err.Error as e:
            print("Database error:", e)
            flash("An error occurred during registration. Please try again.")
            return redirect(url_for('seller_login'))

    else:
        # Required information not found in user_info
        flash("User information incomplete. Please try again.")


# Buyer Registration and Login Routes
@app.route('/buyer_register', methods=['GET', 'POST'])
def buyer_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        phone = request.form.get('phone')
        fname = request.form.get('fname')
        lname = request.form.get('lname')

        # Check if the user already exists
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user_account WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user:
                flash('User already exists. Please log in.')
                return redirect(url_for('login'))
            else:
                # User doesn't exist, register the user
                # Hash the password before storing it
                hashed_password = generate_password_hash(password)
                user_id = generate_user_id("user")
                buyer_id = generate_buyer_id("buyer")
                role = 'buyer'

                cursor.execute('''
                    INSERT INTO user (user_id) 
                    VALUES (%s)
                ''', (user_id,))
                cursor.execute('''
                    INSERT INTO user_account (user_id, email, password, first_name, last_name, role, address, phone) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (user_id, email, hashed_password, fname, lname, role, address, phone))
                connection.commit()

                # Insert buyer details into buyer table
                cursor.execute('''
                    INSERT INTO buyer (user_id, buyer_id) 
                    VALUES (%s, %s)
                ''', (user_id, buyer_id,))
                connection.commit()

                session['user_id'] = user_id
                session['email'] = email
                session['fname'] = fname
                session['lname'] = lname
                session['role'] = role

                flash('Registration successful. Welcome, ' + fname + '!')
                return redirect(url_for('profile'))

    return render_template('register.html')


@app.route('/buyer_login', methods=['GET', 'POST'])
def buyer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user exists and the password is correct
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user_account WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user and check_password(user['password'], password):
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                session['fname'] = user['first_name']
                session['lname'] = user['last_name']
                session['role'] = user['role']

                if user['role'] == 'buyer':
                    session['buyer_id'] = user['buyer_id']
                elif user['role'] == 'seller':
                    session['seller_id'] = user['seller_id']

                flash('Login successful!')
                return redirect(url_for('profile'))
            else:
                flash('Invalid email or password. Please try again.')
                return redirect(url_for('login'))

    return render_template('login.html')

# Seller Registration and Login Routes


@app.route('/seller_register_new', methods=['GET', 'POST'])
def seller_register_new():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        address = request.form.get('address')
        phone = request.form.get('phone')
        fname = request.form.get('fname')
        lname = request.form.get('lname')

        # Check if the user already exists
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user_account WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user:
                flash('User already exists. Please log in.')
                return redirect(url_for('seller_login'))
            else:
                # User doesn't exist, register the user
                # Hash the password before storing it
                hashed_password = generate_password_hash(password)
                user_id = generate_user_id("user")
                seller_id = generate_seller_id("seller")
                role = 'seller'

                cursor.execute('''
                    INSERT INTO user (user_id) 
                    VALUES (%s)
                ''', (user_id,))
                cursor.execute('''
                    INSERT INTO user_account (user_id, email, password, first_name, last_name, role, address, phone) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (user_id, email, hashed_password, fname, lname, role, address, phone))
                connection.commit()

                # Insert seller details into seller table
                cursor.execute('''
                    INSERT INTO seller (user_id, seller_id) 
                    VALUES (%s, %s)
                ''', (user_id, seller_id,))
                connection.commit()

                session['user_id'] = user_id
                session['email'] = email
                session['fname'] = fname
                session['lname'] = lname
                session['role'] = role

                flash('Registration successful. Welcome, ' + fname + '!')
                return redirect(url_for('seller_dashboard'))

    return render_template('seller_register.html')


@app.route('/seller_login_new', methods=['GET', 'POST'])
def seller_login_new():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the user exists and the password is correct
        with connection.cursor() as cursor:
            sql = "SELECT * FROM user_account WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user and check_password(user['password'], password):
                session['user_id'] = user['user_id']
                session['email'] = user['email']
                session['fname'] = user['first_name']
                session['lname'] = user['last_name']
                session['role'] = user['role']

                if user['role'] == 'buyer':
                    session['buyer_id'] = user['buyer_id']
                elif user['role'] == 'seller':
                    session['seller_id'] = user['seller_id']

                flash('Login successful!')
                return redirect(url_for('seller_dashboard'))
            else:
                flash('Invalid email or password. Please try again.')
                return redirect(url_for('seller_login'))

    return render_template('seller_login.html')


def generate_hash(password):
    return generate_password_hash(password)


def check_password(input_password, hashed_password):
    return check_password_hash(hashed_password, input_password)

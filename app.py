import logging
import pymysql.cursors
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, url_for, request, redirect, session, jsonify
from authlib.integrations.flask_client import OAuth
import sqlite3
from db import *
import base64
import requests
import uuid


app = Flask(__name__)
app.secret_key = ("84hrfnsdlkamk93")

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='',  # Enter your MySQL password here
                             database='comrade',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/seller_register')
def seller_register():
    return render_template('seller_register.html')


@app.route('/seller')
def seller():
    return render_template('seller.html')


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/seller_login')
def seller_login():
    return render_template("seller_login.html")


# @app.route('/profile')
# def profile():
#     if 'user_id' in session:
#         return render_template('profile.html', user=session)
#     else:
#         return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        if 'role' in session and session['role'] == 'seller':
            return redirect(url_for('seller_login'))
        else:
            return redirect(url_for('login'))

    try:
        user_id = session['user_id']
        # role = session['role']  # Assuming role is stored in`` session

        # Simplified query (no role check needed)
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

            return render_template('profile.html', user_id=user_id, first_name=first_name, last_name=last_name, email=email, buyer_id=buyer_id, seller_id=seller_id)
        else:
            # Handle case where user_id is in session but no data found (e.g., deleted user)
            return "User data not found"

    except pymysql.err.InterfaceError as e:
        return f"Error connecting to db: {e}"


@app.route('/logout')
def logout():
    # Clear session data
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('fname', None)
    session.pop('lname', None)
    session.pop('role', None)

    # Redirect to login page
    return redirect(url_for('index'))


@app.route('/seller_dashboard')
def seller_dashboard():
    if 'seller_id' in session:
        return render_template('seller_dashboard.html/')
    else:
        return redirect(url_for('seller_login'))


@app.route('/home')
def home():
    try:
        with connection.cursor() as cursor:
            sql = """SELECT p.prod_name, p.condition, p.description, p.seller_id, pi.product_image 
                     FROM Product p 
                     JOIN Product_images pi ON p.product_id = pi.product_id"""
            cursor.execute(sql)
            products = cursor.fetchall()
    except Exception as e:
        print("Error:", e)
    finally:
        print("Success")
        cursor.close()
    return render_template('index.html', products=products)


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
            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))
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
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()
    # Generate unique user ID and buyer ID
    user_id = generate_user_id("user")
    buyer_id = generate_seller_id("buyer")

    if 'email' in user_info:
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

                if user_id and buyer_id:
                    try:
                        # Insert buyer details into buyer table
                        cursor.execute('''
                            INSERT INTO seller (user_id,buyer_id) 
                            VALUES (%s, %s)
                        ''', (user_id, buyer_id,))
                        connection.commit()

                        session['user_id'] = user_id
                        session['email'] = email
                        session['fname'] = fname
                        session['lname'] = lname
                        session['role'] = role
                        # Redirect to profile or any other page
                        return redirect(url_for('profile'))
                    except Exception as e:
                        print("Error:", e)
                        return redirect(url_for('login'))

                else:
                    return "Error: Unable to generate IDs"

        except pymysql.err.InterfaceError as e:
            print("Error connecting to database:", e)
        except pymysql.err.Error as e:
            print("Database error:", e)

    else:
        # Required information not found in user_info
        return "User information incomplete. Please try again."


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


def generate_product_id():
    return str(uuid.uuid4())[:8].upper()


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

    if 'email' in user_info:
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

                if user_id and seller_id:
                    try:
                        # Insert buyer details into buyer table
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
                        # Redirect to profile or any other page
                        return redirect(url_for('seller_dashboard'))
                    except Exception as e:
                        print("Error:", e)
                        return redirect(url_for('seller_login'))

                else:
                    return "Error: Unable to generate IDs"

        except pymysql.err.InterfaceError as e:
            print("Error connecting to database:", e)
        except pymysql.err.Error as e:
            print("Database error:", e)

    else:
        # Required information not found in user_info
        return "User information incomplete. Please try again."


@app.route('/seller_dashboard/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'GET':
        product_name = request.form['product_name']
        category = request.form['category']
        sub_category = request.form['sub_category']
        product_images = request.files.getlist('product_images')
        price = float(request.form['price'])
        description = request.form['description']
        condition = request.form['condition']
        available_units = int(request.form['units'])
        # seller_id = get_seller_id_from_session()

        # product_id = generate_product_id()

        # Database insertion
        # new_product = Product(id=product_id, prod_name=product_name, product_condition=condition, ...)
        # session.add(new_product)
        # session.commit()

        # Update Products page table (explained later)
        # Redirect back to dashboard
        return redirect(url_for('seller_dashboard'))


def insert_product(product_name, product_condition, description, sub_category, units, image_filenames):
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO product (prod_name, prooduct_condition, description, available_units) VALUES (%s, %s, %s, %s)"
            cursor.execute(
                sql, (product_name, product_condition, description, units))
            product_id = cursor.lastrowid
            sql = "INSERT INTO category (category_name) VALUES (%s)"
            cursor.execute(
                sql, (sub_category,))
            category_id = cursor.lastrowid
            sql = "INSERT INTO product_category (product_id, category_id) VALUES (%s, %s)"
            cursor.execute(sql, (product_id, category_id))

            for filename in image_filenames:
                sql = "INSERT INTO Product_Images (product_id, product_image) VALUES (%s, %s)"
                with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as file:
                    image_data = file.read()
                cursor.execute(sql, (product_id, image_data))
            connection.commit()
            return True
    except Exception as e:
        print("Error inserting product:", e)
        return False


@app.route('/seller_add_item', methods=['GET', 'POST'])
def seller_add_item():
    if request.method == 'POST':
        product_name = request.form['productName']
        product_condition = request.form['productCondition']
        sub_category = request.form['subCategory']
        description = request.form['description']
        units = request.form['units']
        images = request.files.getlist('productImages')
        image_filenames = []
        for image in images:
            if image.filename != '':
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['uploads'], filename))
                image_filenames.append(filename)
        if insert_product(product_name, product_condition, sub_category, description, units, image_filenames):
            return redirect(url_for('seller'))
        else:
            return "Error inserting product details"

    return render_template('seller.html')


if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login to add to cart'})

    user_id = session.get('user_id')
    if user_id:
        try:
            product_id = request.json.get('product_id')
            price = session.get('price')  # Assuming you have a way to retrieve the price

def update_cart_count():
    try:
        user_id = session.get('user_id')
        if user_id:
            with connection.cursor() as cursor:
                sql = "SELECT COUNT(*) AS cart_count FROM cart WHERE user_id = %s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                if result:
                    session['cart_count'] = result['cart_count']
                    return result['cart_count']
                else:
                    session['cart_count'] = 0
                    return 0
        else:
            session['cart_count'] = 0
            return 0
    except Exception as e:
        print("Error updating cart count:", e)
        return 0



            with connection.cursor() as cursor:
                # Check if the product is already in the cart
                sql = "SELECT * FROM cart WHERE user_id = %s AND product_id = %s"
                cursor.execute(sql, (user_id, product_id))
                existing_cart_item = cursor.fetchone()

                if existing_cart_item:
                    # If the product is already in the cart, update the quantity
                    sql = "UPDATE cart SET quantity = quantity + 1 WHERE user_id = %s AND product_id = %s"
                    cursor.execute(sql, (user_id, product_id))
                else:
                    # If the product is not in the cart, insert a new entry
                    sql = "INSERT INTO cart (user_id, product_id, quantity, total_price) VALUES (%s, %s, 1, %s)"
                    cursor.execute(sql, (user_id, product_id, price))

                # Update the cart count
                cart_count = update_cart_count()
                return jsonify({'success': True, 'cart_count': cart_count})
        except Exception as e:
            print("Error adding to cart:", e)
            return jsonify({'success': False, 'message': 'An error occurred while adding to cart'})
    else:
        return jsonify({'success': False, 'message': 'User ID not found in session'})

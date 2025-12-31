from flask import Flask, request, render_template, redirect, url_for,session
import pymysql


app = Flask(__name__)
app.secret_key = "secret"
 

def get_db_connection(): 
    return pymysql.connect( 
        host='localhost', 
        user='root', 
        password='root', 
        database='e_commerce' ,
        cursorclass=pymysql.cursors.DictCursor
        )
  
print("Database connected successfully!")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/home')
def about():
    return render_template('index1.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        name = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO app (name, password) VALUES (%s, %s)", (name, password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('login'))
    return render_template('reg.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        name = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM app WHERE name=%s AND password=%s", (name, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['name'] = name
            return redirect(url_for('welcome',name=name))
        else:
           return "Invalid username or password!", "error"
        
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    session_name = session.get('name')
    if session_name:
        return render_template('index1.html')
    else:
        return redirect(url_for('login'))
    
@app.route('/logout') 
def logout(): 
    session.clear()
    return redirect(url_for('home'))

@app.route('/shop')
def shop_page():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM shop")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('shop.html', products=products)

@app.route('/search')
def search():
    query = request.args.get('q', '')  
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if query:  
        cursor.execute("SELECT * FROM shop WHERE name LIKE %s", ("%" + query + "%",))
        products = cursor.fetchall()
    else:
        products = []  

    cursor.close()
    conn.close()

    return render_template('search.html', products=products, query=query)



@app.route('/add_to_heart', methods=['POST'])
def add_to_heart():
    product_id = request.form.get('product_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM heart WHERE product_id=%s", (product_id,))
    existing = cursor.fetchone()

    if not existing:
        cursor.execute("INSERT INTO heart (product_id, quantity) VALUES (%s, %s)", (product_id, 1))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('shop_page'))


@app.route('/wishlist')
def wishlist():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT h.id AS heart_id,
               h.product_id,
               s.name,
               s.price,
               s.image
        FROM heart h
        JOIN shop s ON h.product_id = s.id
        ORDER BY h.id DESC
    """)
    heart_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('heart.html', heart_items=heart_items)

@app.route('/remove_from_heart', methods=['POST'])
def remove_from_heart():
    heart_id = request.form.get('heart_id')
    if not heart_id:
        print("DEBUG remove_from_heart: request.form =", dict(request.form))
        return redirect(url_for('wishlist'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM heart WHERE id=%s", (heart_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('wishlist'))


@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

   
    cursor.execute("SELECT id, quantity FROM cart WHERE product_id=%s", (product_id,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE cart SET quantity=%s WHERE id=%s",
                       (existing['quantity'] + 1, existing['id']))
    else:
        cursor.execute("INSERT INTO cart (product_id, quantity) VALUES (%s, %s)",
                       (product_id, 1))

    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('shop_page'))


@app.route('/cart')
def cart():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("""
        SELECT 
            c.id AS cart_id,
            c.product_id,
            c.quantity,
            s.name,
            s.price,
            s.image
        FROM cart c
        JOIN shop s ON c.product_id = s.id
        ORDER BY c.id DESC
    """)
    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('cart.html', cart_items=cart_items)



@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    cart_id = request.form.get('cart_id') 
    if not cart_id:
        
        print("DEBUG remove_from_cart: request.form =", dict(request.form))
        return redirect(url_for('cart'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE id=%s", (cart_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('cart'))


@app.route('/buy_now', methods=['GET', 'POST'])
def buy_now():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address')
        pincode = request.form.get('pincode')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orders (product_id, quantity, status) VALUES (%s, %s, %s)",
                       (1, 1, 'Address Provided'))   
        order_id = cursor.lastrowid

        cursor.execute(
            "INSERT INTO customer_address (order_id, name, phone, address, pincode) VALUES (%s, %s, %s, %s, %s)",
            (order_id, name, phone, address, pincode)
        )
        conn.commit()
        cursor.close()
        conn.close()

  
        return redirect(url_for('payment', order_id=order_id))

    return render_template('address.html')

@app.route('/payment/<int:order_id>', methods=['GET', 'POST'])
def payment(order_id):
    if request.method == 'POST':
        method = request.form.get('payment_method')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO payments (order_id, method, status) VALUES (%s, %s, %s)",
            (order_id, method, 'Pending')
        )
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('order_success.html', method=method)

    return render_template('payment.html', order_id=order_id)


@app.route('/order_success/<int:product_id>')
def order_success(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM shop WHERE id=%s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('order_success.html', product=product)



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)",(name, email, message))
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('contact_success.html', name=name)

    return render_template('contact.html')



if __name__ == '__main__':
    app.run(debug=True, port=3000)
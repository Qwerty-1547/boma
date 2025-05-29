from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from dotenv import load_dotenv
from functools import wraps
from datetime import timedelta

load_dotenv()
def get_db_connection():
    return pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    cursorclass=pymysql.cursors.DictCursor
)
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(minutes=5)

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        area = request.form['area']
        role = request.form['role']

        password_hash = generate_password_hash(password)
        
        cursor.execute('''INSERT INTO users (full_name, email, phone_number, password_hash, area_id, role_id)
                       VALUES (%s, %s,%s,%s,%s,%s)'''
                       , (full_name,email,phone,password_hash,area,role))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect('/dashboard')
    
    cursor.execute('SELECT id, name FROM areas')
    areas = cursor.fetchall()
    cursor.execute("SELECT * FROM user_roles WHERE role_name != 'Admin'")
    roles = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('register.html', areas=areas, roles=roles)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['full_name']
            session['role_id'] = user['role_id']
            session.permanent = True
            if session.get('role_id') == 1:
                return redirect('/tenant_dashboard')
            elif session.get('role_id') == 2:
                return redirect('/add_house')
            else:
                flash("if not an admin F. OFF")
            return redirect('/login')
        else:
            error = "invalid email address or password"
    return render_template('login.html', error=error)

def login_required(f):  
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
        
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/tenant_dashboard')
@login_required
def tenant_dashboard():
    if session.get('user_id') != 1:
        flash("access denied, available only to logged in tenants")
        return redirect(url_for('dashboard'))
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''SELECT houses.*, areas.name AS area_name, users.full_name AS owner_name
                   FROM bookmarked_houses
                   JOIN houses ON bookmarked_houses.id = houses.id
                   JOIN areas ON houses.area_id = areas.id
                   JOIN users ON houses.owner_id = users.id
                   WHERE bookmarked_houses.user_id = %s''',
                   (session.get('user_id'),))
    bookmarked = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tenant_dashboard.html', bookmarked=bookmarked)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/houses')
def list_houses():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT houses.*, areas.name AS areas_name, users.full_name AS owner_name
        FROM houses
        JOIN areas ON houses.area_id = area_id
        JOIN users ON houses.owner_id = owner_id
        ORDER BY houses.created_at DESC
''')
    houses = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('houses.html', houses=houses)

@app.route('/add_house', methods=['GET', 'POST'])
@login_required
def add_house():
    if session.get('role_id') !=2:
        flash("only owners can add houses.")
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT is_verified FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    if not user or not user['is_verified']:
        flash("Your account is pending verification, contact admin")
        cursor.close()
        conn.close()
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        address = request.form['address']
        area_id = request.form['area_id']

        cursor.execute('''INSERT INTO houses (owner_id, title, description, price, address, area_id)
                       VALUES (%s, %s, %s, %s,%s, %s)''', 
                       (session['user_id'], title, description, price, address, area_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash("House added successfully")
        return redirect(url_for('list_houses'))
    cursor.execute("SELECT id,name FROM areas")
    areas = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('add_house.html', areas=areas)

@app.route('/admin/verify_owners')
@login_required
def verify_owners():
    if session.get('role_id') != 3:
        flash("Admins only")
        return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
SELECT users.id, users.full_name, users.email, users.phone_number, users.area_id, users.created_at
                   FROM users
                   WHERE role_id = 2 AND is_verified = 0
                   ''')
    unverified_owners = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('verify_owners.html', owners = unverified_owners)

@app.route('/admin/approve_owner/<int:user_id>', methods = ['POST'])
@login_required
def approve_owner(user_id):
    if session.get('role_id') != 3:
        flash("Admins only")
        return redirect(url_for('/dashboard'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT role_id, is_verified FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    if not user:
        flash("user not found")
    elif user['role_id'] != 2:
        flash("user not registered as an owner")
    elif user['is_verified']:
        flash("user is already verified")
    else:
        cursor.execute("UPDATE users SET is_verified = 1 WHERE id = %s", (user_id,))
        conn.commit()
        flash("User approved successfully  ")
    cursor.close()
    conn.close()
    return redirect(url_for('verify_owners'))

@app.route('/available_houses')
def available_houses():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''SELECT houses.id, houses.owner_id, users.full_name AS owner_name, houses.title, houses.description, houses.is_available
                   FROM houses
                   JOIN users ON houses.owner_id = users.id 
                   WHERE houses.is_available = 1
                   ORDER BY houses.created_at DESC
                   ''')
    houses= cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('available_houses.html', houses = houses)

#old route handling bookmarking and unbookmarking
'''
@app.route('/bookmark/<int:house_id>', methods = ['POST'])
@login_required
def bookmark_house(house_id):
    user_id = session.get('user_id')
    if session.get('role_id') != 1:
        flash("Only logged in tenants can bookmark houses")
        return redirect(url_for('available_houses'))
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(INSERT INTO bookmarked_houses(user_id, house_id) VALUES(%s,%s), (user_id, house_id))
                       
        conn.commit()
        flash("House bookmarked")

    except pymysql.IntegrityError:
        flash("House already bookmarked")

    cursor.close()
    conn.close()
    return redirect(url_for('available_houses'))'''

@app.route('/toggle_bookmark', methods=['POST'])
@login_required
def toggle_bookmark():
    data = request.get_json()
    house_id = int(data.get('house_id'))

    user_id = session['user_id']
    #house_id = request.json.get('house_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bookmarked_houses WHERE user_id = %s AND house_id = %s", (user_id, house_id))
    bookmark = cursor.fetchone()

    if bookmark:
        cursor.execute("DELETE FROM bookmarked_houses WHERE user_id = %s AND house_id = %s", (user_id, house_id))
        conn.commit()
        result = {"status": "removed"}
    else:
        cursor.execute("INSERT INTO bookmarked_houses (user_id, house_id) VALUES(%s, %s)",(user_id, house_id))
        conn.commit()
        result = {"status": "added"}

    cursor.close()
    conn.close()
    return jsonify(result)
    

app.before_request 
def make_Session_permanent():
    session.permanent= True

if __name__ == '__main__':
    app.run(debug=True)

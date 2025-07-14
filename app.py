from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify, make_response
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename 
import pymysql
import os
from dotenv import load_dotenv
from functools import wraps
from datetime import timedelta, datetime
from decimal import Decimal
import traceback
from jinja2 import TemplateNotFound

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.permanent_session_lifetime = timedelta(hours=1)

import base64
import json

@app.template_filter('b64encode')
def b64encode_filter(s):
    def convert(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    
    #print("[b64encode] used with:", s)
    if isinstance(s, dict):
        s = json.dumps(s, default=convert)
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 5*1024*1024

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1) [1].lower() in ALLOWED_EXTENSIONS


load_dotenv()
def get_db_connection():
    return pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    cursorclass=pymysql.cursors.DictCursor
)


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

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    #handling session caches on browsers
    if 'user_id' in session:
        role_id = session.get('role_id')
        if role_id == 1:
            return redirect('/tenant_dashboard')
        elif role_id == 2:
            return redirect('/owner_dashboard')
        elif role_id == 3:
            return redirect('/admin/verify_owners')
        else:
            session.clear()
            flash("UNAUTHORIZED ACCESS")
            return redirect('/login')
        
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
                return redirect('/owner_dashboard')
            else:
                flash("UNAUTHORIZED ACCESS")
            return redirect('/login')
        else:
            error = "invalid email address or password"
    
    #add no-cache headers on the response
    response = make_response(render_template('login.html', error=error))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['pragma'] = 'no-cache'
    response.headers['expires'] = '0'

    return response

def login_required(f):  
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

#rendering the various sections
@app.route('/section/<section_name>')
@login_required
def section(section_name):
    try:
        return render_template(f'partials/{section_name}.html')
    except TemplateNotFound:
        return "Section not found", 404


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/tenant_dashboard')
@login_required
def tenant_dashboard():
    if session.get('role_id') != 1:
        flash("access denied, available only to logged in tenants")
        return redirect(url_for('dashboard'))
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT users.full_name AS user_name FROM users WHERE users.id = %s", (session.get('user_id'),))
    user_row = cursor.fetchone()
    user_name = user_row['user_name'] if user_row else "Guest"
    last_name = user_name.strip().split()[-1]

    cursor.execute('''SELECT houses.*, areas.name AS area_name, users.full_name AS owner_name
                   FROM bookmarked_houses
                   JOIN houses ON bookmarked_houses.id = houses.id
                   JOIN areas ON houses.area_id = areas.id
                   JOIN users ON houses.owner_id = users.id
                   WHERE bookmarked_houses.user_id = %s''',
                   (session.get('user_id'),))
    bookmarked = cursor.fetchall()

    cursor.execute("SELECT name FROM areas")
    locations = [row['name'] for row in cursor.fetchall()]

    cursor.execute("SHOW COLUMNS FROM houses LIKE 'title'")
    raw_enum = cursor.fetchone()['Type']
    titles = raw_enum.strip("enum()").replace("'", "").split(",")
    #print(locations, titles)
    cursor.execute("SELECT id, name FROM amenities ORDER BY name ASC")
    amenities = cursor.fetchall()
    #print(amenities)
    cursor.close()
    conn.close()
    return render_template('tenant_dashboard.html', bookmarked=bookmarked, user_name=last_name, locations=locations, titles=titles, amenities=amenities)

@app.route('/owner_dashboard')
@login_required
def owner_dashboard():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the user is a verified owner
    cursor.execute('''
        SELECT is_verified FROM users
        WHERE id = %s AND role_id = 2
    ''', (user_id,))
    result = cursor.fetchone()

    if not result:
        cursor.close()
        conn.close()
        flash("Access denied: Only verified owners can access this page.", "danger")
        return redirect(url_for('dashboard'))  # or 'home'

   # is_verified = result[0]
    cursor.execute('SELECT full_name FROM users WHERE id = %s', (user_id,))
    owner_value = cursor.fetchone()
    owner_name = owner_value['full_name'] if owner_value else 'unknown'
    last_name = owner_name.strip().split()[-1]
    # Fetch houses owned by the user
    cursor.execute('''
        SELECT houses.*, areas.name AS area_name,
                   (
                   SELECT image_url
                   FROM house_images
                   WHERE house_images.house_id = houses.id
                   ORDER BY id ASC
                   LIMIT 1)
                   AS image_url
        FROM houses
        JOIN areas ON houses.area_id = areas.id
        WHERE houses.owner_id = %s
        ORDER BY houses.created_at DESC
    ''', (user_id,))
    houses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('owner_dashboard.html', houses=houses, owner_name=last_name) #is_verified=is_verified)

@app.route('/logout', methods=['POST','GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))

#lists available houses for visitors with no accounts
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


@app.route('/partials/houses')
@login_required
def list_houses():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT houses.*, areas.name AS area_name, users.full_name AS owner_name,
                   (
                   SELECT image_url
                   FROM house_images
                   WHERE house_images.house_id = houses.id
                   ORDER BY id ASC
                   LIMIT 1)
                   AS image_filename
        FROM houses
        JOIN areas ON houses.area_id = areas.id
        JOIN users ON houses.owner_id = users.id
        WHERE houses.is_available = 1
        ORDER BY houses.created_at DESC
''')
    houses = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('partials/houses_fragment.html', houses=houses)

@app.route('/house/<int:house_id>/details')
@login_required
def house_details(house_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get house details + owner info
    cursor.execute('''
        SELECT houses.*, 
               areas.name AS area_name,
               users.full_name AS owner_name,
               users.phone_number AS owner_contact,
               users.is_verified AS owner_verified
        FROM houses
        JOIN areas ON houses.area_id = areas.id
        JOIN users ON houses.owner_id = users.id
        WHERE houses.id = %s
    ''', (house_id,))
    house = cursor.fetchone()

    if not house:
        return jsonify({'error': 'House not found'}), 404

    # Get all images for this house
    cursor.execute('''
        SELECT image_url 
        FROM house_images
        WHERE house_id = %s
        ORDER BY id ASC
    ''', (house_id,))
    images = cursor.fetchall()
    image_urls = [img['image_url'] for img in images]

    cursor.close()
    conn.close()

    house['images'] = image_urls

    return jsonify(house)


@app.route('/partials/add_house', methods=['GET'])
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
    cursor.execute("SELECT id, name FROM areas")
    areas = cursor.fetchall()
    cursor.execute("SHOW COLUMNS FROM houses LIKE 'title'")
    enum_raw = cursor.fetchone()['Type']
    title_options = enum_raw.strip("enum()").replace("'", "").split(",")
    #print(title_options)
    cursor.close()
    conn.close()
    return render_template('partials/add_house_fragment.html', areas=areas, titles=title_options)

#uploading houses and images
@app.route('/partials/add_house', methods=['POST'], endpoint='add_house_post')
@login_required
def add_house_post():
    app.logger.info("house post submitted")
    if session.get('role_id') != 2:
        return jsonify({'error':'Only verified owners can add houses'}), 403

    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Login required'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if user is verified
        cursor.execute("SELECT is_verified FROM users WHERE id = %s", (user_id, ))
        user = cursor.fetchone()
        if not user or not user['is_verified']:
            return jsonify({'error': 'Your account is pending verification.'}), 403

        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        address = request.form.get('address')
        area_id = request.form.get('area_id')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except(TypeError, ValueError):
            return jsonify({'Error': 'Invalid coordinates'}), 400
        
        # Validate required fields
        if not all([title, description, price, address, area_id]):
            return jsonify({'error': 'All fields are required'}), 400

        # Validate price
        try:
            price = float(price)
            if price < 0:
                return jsonify({'error': 'Price must be a postive number'}), 400
        except ValueError:
            return jsonify({'error': 'price must be a number'}), 400

        # Handle image upload
        uploaded_files = request.files.getlist('images')
        valid_images = [f for f in uploaded_files if f and f.filename != '' and allowed_file(f.filename)]

        if len(valid_images) < 2:
            return jsonify({'error': 'You must upload at least 2 valid images'}), 400

        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # Insert house record
        cursor.execute('''INSERT INTO houses (owner_id, title, description, price, address, area_id, latitude, longitude)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)''',
                       (session['user_id'], title, description, price, address, area_id, latitude, longitude))
        house_id = cursor.lastrowid

        # Save images and insert into DB
        for file in valid_images:
            filename = secure_filename(file.filename)
            filename = f"{house_id}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(file_path)
            except Exception as e:
                conn.rollback()
                return jsonify({'error': 'Error saving image file'}), 500

            cursor.execute('INSERT INTO house_images (house_id, image_url) VALUES (%s, %s)', (house_id, filename))

        conn.commit()
        return jsonify({'success': 'House added successfully'}), 200
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error adding house: {e}\n{traceback.format_exc()}")
        return jsonify({'error': 'Unexpected error occurred'}), 500

    finally:
        cursor.close()
        conn.close()


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

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    sender_id = session['user_id']
    if not sender_id:
        return jsonify({'status': 'error', 'message': 'Not logged in'}), 401
    receiver_id = data.get('receiver_id')
    house_id = data.get('house_id')  # Optional
    message = data.get('message')

    if not receiver_id or not message:
        return jsonify({'status': 'error', 'message': 'Missing fields'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO messages (sender_id, receiver_id, house_id, message)
        VALUES (%s, %s, %s, %s)
    ''', (sender_id, receiver_id, house_id, message))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'success': True})
    
@app.route('/inbox_data')
@login_required
def inbox_data():
    try:
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT m.id, m.sender_id, m.message, m.house_id, m.sent_at, u.full_name AS sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            LEFT JOIN cleared_notifications c ON c.message_id = m.id AND c.user_id = %s
            WHERE m.receiver_id = %s AND c.message_id is NULL
            ORDER BY m.sent_at DESC
        """, (user_id, user_id))
        rows = cursor.fetchall()

        messages = []
        for row in rows:
            messages.append({
                'id': row['id'],
                'house_id': row['house_id'],
                'message': row['message'],
                'sent_at': row['sent_at'],
                'sender_name': row['sender_name'],
                'sender_id' : row['sender_id']
            })

        cursor.close()
        conn.close()

        return render_template('partials/inbox_fragment.html', messages=messages)
    except Exception as e:
        print("Error in /get_inbox:", e)
        traceback.print_exc()
        return jsonify({'error': 'Server error'}), 500
    
@app.route('/clear_notification', methods=['POST'])
@login_required
def clear_notification():
    data = request.get_json()
    user_id = session['user_id']
    message_id = data.get('message_id')

    if not message_id:
        return jsonify({'success': False, 'error': 'Missing message ID'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT IGNORE INTO cleared_notifications (user_id, message_id)
                       VALUES (%s, %s)
                       """, (user_id, message_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print("error in clear_notification", e)
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': 'DB error'}), 500
    
    cursor.close()
    conn.close()
    return jsonify({'success': True})

@app.route('/filter_houses', methods=['POST'])
@login_required
def filter_houses():
    filters = request.get_json()
    title = filters.get('title', '').strip()
    location = filters.get('location', '').strip()
    min_price = filters.get('min_price')
    max_price = filters.get('max_price')
    amenity_ids = filters.get('amenities', [])
    if isinstance(amenity_ids, str):
        amenity_ids = [int(a.strip()) for a in amenity_ids.split(',') if a.strip().isdigit()]

    conn = get_db_connection()
    cursor = conn.cursor()

    house_ids_with_amenities = []
    if amenity_ids:
        placeholders = ','.join(['%s'] * len(amenity_ids))
        count_required = len(amenity_ids)
        subquery = f'''
        SELECT house_id
        FROM house_amenities
        WHERE amenity_id IN ({placeholders})
        GROUP BY house_id
        HAVING COUNT(DISTINCT amenity_id) = {count_required}
        '''
        cursor.execute(subquery, amenity_ids)
        results = cursor.fetchall()
        house_ids_with_amenities = [row['house_id'] for row in results]


    query = '''
        SELECT houses.*, areas.name AS area_name, users.full_name AS owner_name,
        (
        SELECT image_url
        FROM house_images
        WHERE house_images.house_id = houses.id
        ORDER BY id ASC
        LIMIT 1
        ) AS image_filename
    FROM houses
    JOIN areas ON houses.area_id = areas.id
    JOIN users ON houses.owner_id = users.id
    WHERE houses.is_available = 1
    '''
    params = []
    if title:
        query += 'AND houses.title LIKE %s'
        params.append(f'%{title}%')

    if location:
        query += 'AND areas.name LIKE %s'
        params.append(f'%{location}%')

    if min_price:
        query += 'AND houses.price >= %s'
        params.append(min_price)

    if max_price:
        query += 'AND houses.price <= %s'
        params.append(max_price)

    if amenity_ids:
        if house_ids_with_amenities:
            placeholders = ','.join(['%s'] * len(house_ids_with_amenities))
            query += f' AND houses.id IN ({placeholders})'
            params.extend(house_ids_with_amenities)
        else:
            return render_template('partials/houses_fragment.html', houses=[])
        

    cursor.execute(query, params)
    houses = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('partials/houses_fragment.html', houses=houses)

app.before_request 
def make_Session_permanent():
    session.permanent= True

if __name__ == '__main__':
    app.run(debug=True)

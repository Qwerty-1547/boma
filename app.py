from flask import Flask, render_template, request, redirect, session, url_for, flash
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os
from dotenv import load_dotenv


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
        return redirect('/success')
    
    cursor.execute('SELECT id, name FROM areas')
    areas = cursor.fetchall()
    cursor.execute('SELECT id, role_name FROM user_roles')
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
            return redirect('/dashboard')
        else:
            error = "invalid email address or password"
    return render_template('login.html', error=error)
        

if __name__ == '__main__':
    app.run(debug=True)

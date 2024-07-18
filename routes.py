from flask import Blueprint, render_template, request, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash

routes = Blueprint('user', __name__)

@routes.route('/tours')
def tours():
    return render_template('tours.html')

@routes.route('/account')
def account():
    return render_template('account.html')

@routes.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        password = generate_password_hash(request.form['password'])

        with sqlite3.connect('wonderlust_tours.db') as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO users (username, email, first_name, last_name, phone_number, password) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, email, first_name, last_name, phone_number, password))
            conn.commit()
        
        return redirect(url_for('index'))
    
    return render_template('register.html')

@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect('wonderlust_tours.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cur.fetchone()
            if user and generate_password_hash(user[5], password):
                session['user_id'] = user[0]
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password')

    return render_template('login.html')

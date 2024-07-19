from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3
import secrets

routes = Blueprint('user', __name__)
routes.secret_key = secrets.token_urlsafe(24)


# Getting connection to database
def get_db_connection():
    conn = sqlite3.connect('wonderlust_tours.db')
    conn.row_factory = sqlite3.Row
    return conn


# Registering user or admin
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

<<<<<<< HEAD
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
=======

# Login for user or admin
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('tours'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')


# Logout user or admin
@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


# Tours page with cards and booking option
@routes.route('/tours')
def tours():
    conn = get_db_connection()
    tours = conn.execute('SELECT * FROM tours').fetchall()
    conn.close()
    return render_template('tours.html', tours=tours)


# Booking logic for selected tour
@routes.route('/book/<int:tour_id>')
def book(tour_id):
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user_id = session['user_id']
    with sqlite3.connect('wonderlust_tours.db') as conn:
        cur = conn.cursor()
        # Fetch tour information
        cur.execute("SELECT * FROM tours WHERE id = ?", (tour_id,))
        tour = cur.fetchone()
        # Retrieve user information
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()

        if not tour:
            return "Tour not found", 404
        cur.execute("INSERT INTO booking (user_id, tour_id, status) VALUES (?, ?, ?)",
                    (user_id, tour_id, 'pending'))
        conn.commit()
    
    return render_template('book.html', tour=tour, user=user)


# My account 
@routes.route('/account')
def account():
    return render_template('account.html')
>>>>>>> 0b2d3638cb59835b6de59db2ca169d18770ba181

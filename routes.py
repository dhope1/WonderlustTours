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

# Routes for the admin 
@routes.route('/admin/dashboard')
def dashboard():
    conn = get_db_connection()
    tours = conn.execute('SELECT * FROM tours').fetchall()
    total_tours = len(tours)
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_bookings = conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0]
    conn.close()

    context = {
        'tours': tours,
        'total_tours': total_tours,
        'total_users' : total_users,
        'total_bookings': total_bookings
    }
    return render_template('admin/dashboard.html', tours=tours, total_tours=total_tours, total_users=total_users, total_bookings=total_bookings)

# Adding tours
@routes.route('/admin/add_tour', methods=['GET', 'POST'])
def addTour():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        location = request.form['location']
        image_filename = request.form['image_filename']
        
        with sqlite3.connect('wonderlust_tours.db') as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO tours (title, description, price, location, image_filename) 
                VALUES (?, ?, ?, ?, ?)
            ''', (title, description, price, location, image_filename))
            conn.commit()
        
        # flash('Tour added successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('admin/create_tours_form.html')


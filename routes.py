from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

import sqlite3

routes = Blueprint('user', __name__)

# Getting connection to database
def get_db_connection():
    conn = sqlite3.connect('wonderlust_tours.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to fetch tours from the database
def get_tours_from_db():
    conn = get_db_connection()
    tours = conn.execute('SELECT id, title, description, price, location, image_filename FROM tours').fetchall()
    conn.close()
    return tours

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
        flash('Siccess, registration successful, procced to login')
        return redirect(url_for('user.login'))
    
    return render_template('register.html')

# Login for user or admin
@routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            if '@admin' in email:
                flash('Success, welcome to the admin dashboard')
                return redirect(url_for('user.dashboard'))
            else:
                flash('Success, welcome to the tours page')
                return redirect(url_for('user.tours'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

# Logout user or admin
@routes.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('user.login'))

# Tours page with cards and booking option
@routes.route('/tours')
def tours():
    tours = get_tours_from_db()
    return render_template('tours.html', tours=tours)

# API endpoint to fetch tours
@routes.route('/api/tours', methods=['GET'])
def get_tours():
    tours = get_tours_from_db()
    tour_list = [
        {
            'id': tour['id'],
            'title': tour['title'],
            'description': tour['description'],
            'price': tour['price'],
            'location': tour['location'],
            'image_filename': tour['image_filename']
        }
        for tour in tours
    ]
    return jsonify(tour_list)

# Booking logic for selected tour
@routes.route('/book/<int:tour_id>', methods=['GET', 'POST'])
def book(tour_id):
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        tour_title = request.form['tour_title']
        location = request.form['location']
        price = request.form['price']
        username = request.form['username']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        date_of_booking = request.form['date_of_booking']
        
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
            
            cur.execute("INSERT INTO bookings (user_id, tour_id, status, title, location, price, username, email, first_name, last_name, date_of_booking) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (user_id, tour_id, 'pending', tour_title, location, price, username, email, first_name, last_name, date_of_booking))
            conn.commit()
            flash('Booking successful, proceed to check your booking status')
        
        return redirect(url_for('user.tour_details', tour_id=tour_id))
    
    with sqlite3.connect('wonderlust_tours.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tours WHERE id = ?", (tour_id,))
        tour = cur.fetchone()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
    
    return render_template('book.html', tour=tour, user=user)


@routes.route('/tour_details/<int:tour_id>')
def tour_details(tour_id):
    if 'user_id' not in session:
        return redirect(url_for('user.login'))
    
    user_id = session['user_id']
    
    with sqlite3.connect('wonderlust_tours.db') as conn:
        conn.row_factory = sqlite3.Row  # This will return rows as dictionaries
        cur = conn.cursor()
        
        # Fetch tour information
        cur.execute("SELECT * FROM tours WHERE id = ?", (tour_id,))
        tour = cur.fetchone()
        
        # Retrieve user information
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cur.fetchone()
        
        # Retrieve bookings made by the user
        cur.execute("""
            SELECT b.*, t.title, t.location, t.price
            FROM bookings b
            JOIN tours t ON b.tour_id = t.id
            WHERE b.user_id = ?
        """, (user_id,))
        bookings = cur.fetchall()
    
    return render_template('tourdetails.html', tour=tour, user=user, bookings=bookings)






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
        
        flash('Tour added successfully!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('admin/create_tours_form.html')

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from config import mail
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from flask import url_for

import io
import os
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
        flash('Success, registration successful, procced to login', 'success')
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
                flash('Success, welcome to the tours page', 'success')
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
        flash('Please log in to book a tour.', 'warning')
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
            flash('Booking successful, proceed to check your booking status', 'success')

            # Send email
            msg = Message("Wonderlust Tours Booking", recipients=[email])
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                    }}
                    .header {{
                        background-color: #ffebcc;
                        padding: 10px;
                        text-align: center;
                        border-bottom: 2px solid #ffa500;
                    }}
                    .content {{
                        margin: 20px;
                    }}
                    .details {{
                        background-color: #f9f9f9;
                        padding: 15px;
                        border: 1px solid #ddd;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 0.9em;
                        color: #888;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <img src="cid:logo" style="max-width: 200px;" alt="Wonderlust Tours Logo" />
                    <h2>Booking Pending</h2>
                </div>
                <div class="content">
                    <h3>Dear {first_name} {last_name},</h3>
                    <p>Thank you for booking with us! You have successfully booked the tour '<strong>{tour_title}</strong>' at <strong>{location}</strong> on <strong>{date_of_booking}</strong>.</p>
                    <div class="details">
                        <p><strong>Tour Details:</strong></p>
                        <ul>
                            <li>Tour name: <strong>{tour_title}</strong></li>
                            <li><strong>Price:</strong> {price}</li>
                            <li><strong>Location:</strong> {location}</li>
                            <li><strong>Date:</strong> {date_of_booking}</li>
                            <li><strong>Booking status:</strong> Pending</li>
                        </ul>
                    </div>
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    <p>We look forward to welcoming you!</p>
                    <div class="footer">
                        <h4>Best regards,</h4>
                        <h1>Wonderlust Tours</h1>
                    </div>
                </div>
            </body>
            </html>
            """
            with routes.open_resource("static/images/logo.jpg") as logo:
                msg.attach("logo.jpg", "image/jpeg", logo.read(), 'inline', headers={'Content-ID': '<logo>'})
            mail.send(msg)
            flash('Kindly check your email for further details', 'info')

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
        conn.row_factory = sqlite3.Row
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




#################################

# Routes for the admin start here

# ################################


# Admin dashboard routes
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


# Routes for accessing edit tour page
@routes.route('/admin/tours/edit/<int:tour_id>', methods=['GET'])
def edit_tour(tour_id):

    with sqlite3.connect('wonderlust_tours.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tours WHERE id = ?", (tour_id,))
        tour = cur.fetchone()

    if not tour:
        return "Tour not found", 404

    return render_template('admin/edit_tours.html', tour=tour)


# Routes for updating/editing tour
@routes.route('/admin/tours/edit/<int:tour_id>', methods=['POST'])
def update_tour(tour_id):
    title = request.form['title']
    location = request.form['location']
    price = request.form['price']
    description = request.form['description']

    with sqlite3.connect('wonderlust_tours.db') as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE tours
            SET title = ?, location = ?, price = ?, description = ?
            WHERE id = ?
        """, (title, location, price, description, tour_id))
        conn.commit()

    flash('Tour updated successfully')
    return redirect(url_for('user.dashboard'))

# Routes for deleting tour
@routes.route('/admin/tours/delete/<int:tour_id>', methods=['GET', 'POST'])
def delete_tour(tour_id):

    if request.method == 'POST':
        with sqlite3.connect('wonderlust_tours.db') as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM tours WHERE id = ?", (tour_id,))
            conn.commit()
            flash('Tour deleted successfully')
        return redirect(url_for('user.dashboard'))

    with sqlite3.connect('wonderlust_tours.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tours WHERE id = ?", (tour_id,))
        tour = cur.fetchone()

    if not tour:
        return "Tour not found", 404

    return render_template('admin/delete_tour.html', tour=tour)

# Routes for booking page
@routes.route('/admin/bookings')
def bookings():
    with sqlite3.connect('wonderlust_tours.db') as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Count total bookings, accepted bookings, and pending bookings
        cur.execute("SELECT COUNT(*) FROM bookings")
        total_booking_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM bookings WHERE status = 'accepted'")
        confirmed_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM bookings WHERE status = 'pending'")
        total_pending = cur.fetchone()[0]

        # Fetch all bookings
        cur.execute("SELECT * FROM bookings")
        bookings = cur.fetchall()

        # Fetch pending requests
        cur.execute("SELECT * FROM bookings WHERE status = 'pending'")
        pending_requests = cur.fetchall()

        # Fetch accepted requests
        cur.execute("SELECT * FROM bookings WHERE status = 'accepted'")
        confirmed = cur.fetchall()

        # Fetch all requests
        cur.execute("SELECT * FROM bookings")
        all_requests = cur.fetchall()

    
    return render_template('admin/bookings.html', confirmed_count=confirmed_count, pending_requests=pending_requests, confirmed=confirmed, all_requests=all_requests, total_booking_count=total_booking_count,  total_pending=total_pending)



# Routes for cofirming a booking
@routes.route('/admin/confirm_booking/<int:booking_id>', methods=['GET', 'POST'])
def confirm_booking(booking_id):
    if request.method == 'POST':
        with sqlite3.connect('wonderlust_tours.db') as conn:
            cur = conn.cursor()
            cur.execute("UPDATE bookings SET status = 'accepted' WHERE id = ?", (booking_id,))
            conn.commit()

            cur.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
            booking = cur.fetchone()

            if booking:
                email = booking[8]
                first_name = booking[9]
                last_name = booking[10]
                tour_title = booking[4]
                location = booking[5]
                price = float(booking[6]) 
                date_of_booking = booking[11]

                # Generate PDF receipt
                buffer = io.BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                elements = []

                # Add logo and header
                logo_path = 'static/images/logo.jpg'
                try:
                    logo = Image(logo_path, width=100, height=100)
                    elements.append(logo)
                except Exception as e:
                    print(f"Error loading logo: {e}")

                elements.append(Spacer(1, 12))
                elements.append(Paragraph("<b>Wonderlust Tours</b>", getSampleStyleSheet()['Title']))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph(f"<b>Booking Confirmation Receipt</b>", getSampleStyleSheet()['Heading2']))
                elements.append(Spacer(1, 24))

                # Add booking details
                details = [
                    ("Booking ID:", booking_id),
                    ("Tour:", tour_title),
                    ("Location:", location),
                    ("Date:", date_of_booking),
                    ("Price:", f"${price:.2f}")
                ]
                for label, value in details:
                    elements.append(Paragraph(f"<b>{label}</b> {value}", getSampleStyleSheet()['BodyText']))
                    elements.append(Spacer(1, 12))

                elements.append(Spacer(1, 24))

                # Add pricing table
                table_data = [
                    ["Description", "Amount"],
                    [tour_title, f"${price:.2f}"],
                    ["Total", f"${price:.2f}"]
                ]
                table = Table(table_data, colWidths=[200, 100])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                elements.append(table)

                elements.append(Spacer(1, 48))

                # Footer
                elements.append(Paragraph("Thank you for your booking!", getSampleStyleSheet()['BodyText']))
                elements.append(Paragraph("Contact us: contact@wonderlusttours.com", getSampleStyleSheet()['BodyText']))

                doc.build(elements)

                buffer.seek(0)
                pdf_data = buffer.getvalue()
                buffer.close()

                msg = Message("Booking Confirmation and Receipt", recipients=[email])
                msg.body = f"Dear {first_name} {last_name},\n\nYour booking for '{tour_title}' at '{location}' has been confirmed.\n\nPlease find your receipt attached.\n\nThank you!"
                msg.attach(f"receipt_{booking_id}.pdf", "application/pdf", pdf_data)
                mail.send(msg)

            flash('Booking confirmed successfully. Confirmation email sent.')
            return redirect(url_for('user.bookings'))

    with sqlite3.connect('wonderlust_tours.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        booking = cur.fetchone()

    if not booking:
        flash('Booking not found.')
        return redirect(url_for('bookings'))

    booking_dict = {
        'id': booking[0],
        'title': booking[3],
        'username': booking[6],
        'location': booking[4],
        'price': booking[5],
    }

    return render_template('admin/confirm_tour.html', booking=booking_dict)


# Routes for denying booking
@routes.route('/admin/deny_tour/<int:booking_id>', methods=['GET', 'POST'])
def deny_booking(booking_id):
    if request.method == 'POST':
        with sqlite3.connect('wonderlust_tours.db') as conn:
            cur = conn.cursor()
            cur.execute("UPDATE bookings SET status = 'denied' WHERE id = ?", (booking_id,))
            conn.commit()

            # Fetch booking details to include in the email
            cur.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
            booking = cur.fetchone()

            if booking:
                email = booking[8]
                first_name = booking[9]
                last_name = booking[10]
                tour_title = booking[4]
                location = booking[5]
                date_of_booking = booking[11]

                # Send rejection email with logo
                msg = Message("Wonderlust Tours Booking Rejected", recipients=[email])
                msg.html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                        }}
                        .header {{
                            background-color: #ffcccc;
                            padding: 10px;
                            text-align: center;
                            border-bottom: 2px solid #dd0000;
                        }}
                        .content {{
                            margin: 20px;
                        }}
                        .details {{
                            background-color: #f9f9f9;
                            padding: 15px;
                            border: 1px solid #ddd;
                        }}
                        .footer {{
                            margin-top: 20px;
                            font-size: 0.9em;
                            color: #888;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <img src="cid:logo" style="max-width: 200px;" alt="Wonderlust Tours Logo" />
                        <h2>Booking Rejected</h2>
                    </div>
                    <div class="content">
                        <h3>Dear {first_name} {last_name},</h3>
                        <p>We regret to inform you that your booking for the tour '<strong>{tour_title}</strong>' at <strong>{location}</strong> on <strong>{date_of_booking}</strong> has been <span style="color: red;"><strong>rejected</strong></span>.</p>
                        <div class="details">
                            <p><strong>Tour Details:</strong></p>
                            <ul>
                                <li>Tour name: <strong>{tour_title}</strong></li>
                                <li><strong>Location:</strong> {location}</li>
                                <li><strong>Date:</strong> {date_of_booking}</li>
                                <li><strong>Booking status:</strong> Rejected</li>
                            </ul>
                        </div>
                        <p>If you have any questions or need further assistance, please don't hesitate to contact us.</p>
                        <p>We apologize for any inconvenience caused.</p>
                        <div class="footer">
                            <h4>Best regards,</h4>
                            <h1>Wonderlust Tours</h1>
                        </div>
                    </div>
                </body>
                </html>
                """
                with routes.open_resource("static/images/logo.jpg") as logo:
                    msg.attach("logo.jpg", "image/jpeg", logo.read(), 'inline', headers={'Content-ID': '<logo>'})
                mail.send(msg)

            flash('Tour request denied successfully. Notification email sent to the user.')
            return redirect(url_for('user.bookings'))

    with sqlite3.connect('wonderlust_tours.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        booking = cur.fetchone()

    if not booking:
        flash('Booking not found.')
        return redirect(url_for('user.bookings'))

    booking_dict = {
        'id': booking[0],
        'title': booking[4],
        'username': booking[7]
    }

    return render_template('admin/deny_tour.html', booking=booking_dict)
from flask import Flask, render_template, request, redirect, url_for
from routes import routes
import sqlite3
import secrets
from flask_mail import Mail, Message
from config import mail

app = Flask(__name__)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'olowophilly77@gmail.com'
app.config['MAIL_PASSWORD'] = 'vebi xkhx lntp ksjr'
app.config['MAIL_DEFAULT_SENDER'] = 'olowophilly77@gmail.com'

mail.init_app(app)

# Database setup
def init_db():
    with sqlite3.connect('wonderlust_tours.db') as conn:
        with open('schema.sql') as f:
            conn.executescript(f.read())

# Initialize the database
init_db()
print("Database Initialization Successful")


# Set the secret key to a random value
app.secret_key = secrets.token_urlsafe(24)

# Register blueprints
app.register_blueprint(routes)

@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True, port=5005)
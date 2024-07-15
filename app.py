from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# Database setup
def init_db():
    with sqlite3.connect('wonderlust_tours.db') as conn:
        with open('schema.sql') as f:
            conn.executescript(f.read())

# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5005)
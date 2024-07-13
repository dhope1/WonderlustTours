#from app import create_app
from flask import Flask, render_template

#app = create_app()
app = Flask(__name__)



@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/sheve')
def sheve():
    return f"Heyy"


if __name__ == "__main__":
    app.run(debug=True, port=5002)

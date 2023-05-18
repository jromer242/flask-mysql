# https://peps.python.org/pep-0249/#commit
from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
from pymysql.connections import Connection
import pymysql
import pymysql.cursors

import re

mysql = MySQL()

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = 'connection'

# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='2415'
app.config['MYSQL_DB'] = 'pythonlogin'

# Intialize MySQL - flask_ext
mysql.init_app(app)

# http://127.0.0.1:5000/pythonlogin/ - this will be the login page, we need to use both GET and POST requests
@app.route('/')
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = 'I hope this works'
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        
        # Check if account exists using MySQL
        # using pymysql to connect in place of MySQLdb
        # conn = pymysql.connect("localhost","root","2415","pythonlogin" )
            # pymysql.connect() works 
        conn = pymysql.connect(host = "localhost", user="root", password="2415", database="pythonlogin")
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # important to my change - Create a new connection and cursor that returns rows as dictionaries
        # conn = mysql.connect()
        # cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
        # Close the cursor and connection
        conn.close()
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# http://127.0.0.1:5000/pythonlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = pymysql.connect(host = "localhost", user="root", password="2415", database="pythonlogin")
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
        # Close the cursor and connection
        # conn.close()
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            # To use commit you need to import from pymysql.connections import Connection
            #  takes the same arguments and some as pymysql.connect()
            connection = Connection(host = "localhost", user="root", password="2415", database="pythonlogin")
            # to commit create the instance of the class Connection else TypeError: Missing 1 required positional argument: 'self'
            connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

#  http://127.0.0.1:5000/pythonlogin/home
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        conn = pymysql.connect(host = "localhost", user="root", password="2415", database="pythonlogin")
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
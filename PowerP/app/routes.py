from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User
from werkzeug.urls import url_parse


from flask import Flask, request, jsonify
import mysql.connector

#This can and probably should be changed to /Home, but keep @app.route('/') to display home page when no route is entered or directed to
@app.route('/')
@app.route('/index')
@login_required
def index():
    devices = [
        {
            'owner':{'username':'Stoff'},
            'Device_Name': 'Its a random serial number?'
        },
        {
            'owner':{'username':'Power'},
            'Device_Name':'Partners123'
        }
    ]
    return render_template("index.html", title='Home Page', devices=devices)


#Login route, verifies if the usrer isn't already logged in or if the correct information is supplied
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page =url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

#Logs the user out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#Route to register user, if requirements are met user is created and added to the db, then user is redirected to login page
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username= form.username.data, email= form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User registrated, Welcome to Power Partners! In order to view device data ensure that all your devices are added')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/Home')
def Home():
    return render_template("Home.html", title='HomePage')

@app.route('/Summary')
def DSUm():
    return render_template("DailySummary.html", title='Summary Page')

#### DB Setup, Note this is just a test db and the correct DB is setup in the config.py #####
# The reason for this DB is just for testing purposes
servername = "127.0.0.1"
username = "root"
password = "PowerPartners1"
dbname = "SystemSchema"


#########    Hourly flask start       ######
#Hourly flask query data and return json
@app.route('/hourly', methods=['POST'])
def get_hourly_data():

    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    # Filter the data for the date supplied by the user
    selected_date = request.form.get('selected-date')
    query = "SELECT generated_power,date,consumed_power,excess_power FROM HourlySummary WHERE date BETWEEN %s AND %s"
    query_params = (f"{selected_date} 00:00:00", f"{selected_date} 23:00:00")
    cursor.execute(query, query_params)
    result = cursor.fetchall()

    # Close the database connection
    cursor.close()
    cnx.close()

    # Create a list of dictionaries to store the data
    data = [{'generated_power': row[0], 'date': row[1], 'consumed_power': row[2], 'excess_power': row[3]} for row in result]

    # Return the data as JSON
    return jsonify(data)

# Render Hourly javascript and return rendered html
@app.route('/renHourly')
def renHourly():
    return render_template("Hourly.html")
#########    Hourly flask End       ######


#########    Daily flask start       ######
#Daily flask query data and return json
@app.route('/daily', methods=['POST'])
def get_daily_data():

    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    # Filter the data for the date supplied by the user
    selected_date = request.form.get('selected-date')
    query = "SELECT generated_power_sum,DATE(date) AS date,consumed_power_sum,excess_power_sum FROM DailySummary WHERE MONTH(date) = MONTH(%s)"
    cursor.execute(query, (selected_date,))
    result = cursor.fetchall()

    # Close the database connection
    cursor.close()
    cnx.close()

    # Create a list of dictionaries to store the data
    data = [{'generated_power_sum': row[0], 'date': row[1].strftime('%Y-%m-%d'), 'consumed_power_sum': row[2], 'excess_power_sum': row[3]} for row in result]

    # Return the data as JSON
    return jsonify(data)

# Render Daily javascript and return rendered html
@app.route('/renDaily')
def renDaily():
    return render_template("daily.html")
#########    daily flask End       ######


#########    Monthly flask start       ######
#Monthly flask query data and return json
@app.route('/monthly', methods=['POST'])
def get_monthly_data():

    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    # Filter the data for the date supplied by the user
    selected_date = request.form.get('selected-date')
    query = "SELECT generated_power_sum,year,month,consumed_power_sum,excess_power_sum FROM MonthlySummary m WHERE m.year = Year(%s)"
    cursor.execute(query, (selected_date,))
    result = cursor.fetchall()

    # Close the database connection
    cursor.close()
    cnx.close()

    # Create a list of dictionaries to store the data
    data = [{'generated_power_sum': row[0], 'year': row[1],'month':row[2], 'consumed_power_sum': row[3], 'excess_power_sum': row[4]} for row in result]

    # Return the data as JSON
    return jsonify(data)

# Render Monthly javascript and return rendered html
@app.route('/renMonthly')
def renMonthly():
    return render_template("monthly.html")
#########    Monthly flask End       ######
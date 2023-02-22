from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User,Device,Hourly_Summary,Daily_Summary,Monthly_Summary
from werkzeug.urls import url_parse


from flask import Flask, request, jsonify
import mysql.connector

#Debug using:
#print(ValueToPrint, file=sys.stderr)

import sys

defaultDate="2021-01-01"
devName= None
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
    users = db.session.query(User).all()
    Devicess = db.session.query(Device).all()
    Hourly_Summaries = db.session.query(Hourly_Summary).all()
    print(Devicess,file = sys.stderr)
    print(Hourly_Summaries,file=sys.stderr)
    print(users,file=sys.stderr)
    if current_user.is_authenticated:
        return redirect(url_for('Home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page =url_for('Home')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/login2')
def login2():
    return render_template('login2.html')
@app.route('/loginInfo', methods=['POST'])
def loginInfo():
    user = User.query.filter_by(username=request.form['username']).first()
    if user is None or not user.check_password(request.form['password-field']):
        flash('Invalid username or password')
        return redirect(url_for('login'))
    login_user(user, remember=False)
    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page =url_for('Home')
    return redirect(next_page)



#Logs the user out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Home'))

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


#### DB Setup, Note this is just a test db and the correct DB is setup in the config.py #####
# The reason for this DB is just for testing purposes
servername = "127.0.0.1"
username = "root"
password = "PowerPartners1"
dbname = "PP_DB"


@app.route('/Summary',methods=['GET','POST'])
@login_required
def DSUm():
        # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()


    # Filter the data for the date supplied by the user
    """ user_id = current_user.id
    query = "SELECT * FROM Devices WHERE user_id = %s"
    cursor.execute(query, (current_user.id,))
    devices = [{'device_name': row[0], 'device_id': row[1]} for row in cursor.fetchall()]

    if request.method == 'POST':
        device_serial = request.form['device']
        query = "SELECT id FROM Devices WHERE name = %s"
        cursor.execute(query, device_serial)
        device_id = cursor.fetchall()
        
       # return render_template('summary.html', devices=devices, selected_device=selected_device, hourly_data=hourly_data) """
    

    # Get a list of the user's devices from the database
    selected_date = request.form.get('selected-date')
    session['selected_date'] = selected_date
    
    selected_device = request.form.get('device_name') or session.get('selected_device')
    devName= request.form.get('device_name') or session.get('selected_device')
    session['selected_device'] =selected_device
    

     
    query = "SELECT serial, id FROM device WHERE user_id = %s"
    cursor.execute(query, (current_user.id,))
    devices = [{'device_name': row[0], 'device_id': row[1]} for row in cursor.fetchall()]
    if session.get('selected_device')==None:
        session['selected_device'] = devices[0]["device_name"]
        devName =devices[0]["device_name"]

    if session.get('selected_date')==None:
        session['selected_date'] = "2021-01-02"
    print(session.get('selected_date') + " Summary", file=sys.stderr)
    print(session.get('selected_device') + " Summary device sent", file=sys.stderr)
    return render_template("DailySummary.html", title='Summary Page',devices=devices)

@app.route('/summaryP',methods=['POST'])
def SummaryPost():
    selected_date = request.form.get('selected-date')
    selected_device = request.form.get('device_name')
    session['selected_date'] = selected_date
    session['selected_device'] =selected_device
    print(selected_date, file=sys.stderr)
    print(selected_device, file=sys.stderr)
    return None

#########    Hourly flask start       ######
#Hourly flask query data and return json
@app.route('/hourly', methods=['POST'])
def get_hourly_data():

    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    # Filter the data for the date supplied by the user
    selected_date = request.form.get('selected-date') or session.get('selected_date')
    device_name = devName or session.get('selected_device')

    device_name= session.get('selected_device')

    print(device_name + " Hourly device sent", file=sys.stderr)
    query = "SELECT generated_power, date, consumed_power, excess_power FROM hourly__summary hs JOIN device d ON hs.device_id = d.id WHERE hs.date BETWEEN %s AND %s AND d.serial = %s"
    query_params = (f"{selected_date} 00:00:00", f"{selected_date} 23:00:00", device_name)
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
#----------    Hourly flask End   --------#


#########    Daily flask start       ######
#Daily flask query data and return json
@app.route('/daily',  methods=['POST'])
def get_daily_data():
    """
    Skryf code om die volgende te doen (Die code is om die current user se id tekry, dan die device wat daai current user match en dan die data vir daai device en die selected date)
    User{}=Select * From User where username = current.user
    UDevice= Select DeviceID From Device where User_ID = User[ID]
    Select * From hourly where hourl.Device_ID = UDevice AND Date = SelectedDate
    """
    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()
    #print(session.get('selected_date'), file=sys.stderr)
    # Filter the data for the date supplied by the user
    selected_date = session.get('selected_date')
    device_name = devName or session.get('selected_device')



    query = "SELECT generated_power_sum,DATE(date) AS date,consumed_power_sum,excess_power_sum FROM daily__summary ds JOIN device d ON ds.device_id = d.id WHERE MONTH(ds.date) = MONTH(%s) AND d.serial = %s"
    cursor.execute(query, (selected_date,device_name))
    result = cursor.fetchall()

    # Close the database connection
    cursor.close()
    cnx.close()

    # Create a list of dictionaries to store the data
    data = [{'generated_power_sum': row[0], 'date': row[1].strftime('%Y-%m-%d'), 'consumed_power_sum': row[2], 'excess_power_sum': row[3]} for row in result]

    # Return the data as JSON
    return jsonify(data)

# Render Daily javascript and return rendered html
@app.route('/renDaily', methods=['GET'])
def renDaily():
    return render_template("daily.html")
#-------------    daily flask End   ----------#


#########    Monthly flask start       ######
#Monthly flask query data and return json
@app.route('/monthly', methods=['POST'])
def get_monthly_data():

    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    # Filter the data for the date supplied by the user
    selected_date = session.get('selected_date')
    device_name = devName or session.get('selected_device')

    """ SELECT generated_power, date, consumed_power, excess_power FROM hourly__summary hs JOIN device d ON hs.device_id = d.id WHERE hs.date BETWEEN %s AND %s AND d.serial = %s
    """
    #print(session.get('selected_date'), file=sys.stderr)
    query = "SELECT generated_power_sum,year,month,consumed_power_sum,excess_power_sum FROM monthly__summary ms JOIN device d ON ms.device_id = d.id WHERE ms.year = Year(%s) AND d.serial = %s"
    cursor.execute(query, (selected_date,device_name))
    result = cursor.fetchall()

    # Close the database connection
    cursor.close()
    cnx.close()

    # Create a list of dictionaries to store the data
    data = [{'generated_power_sum': row[0], 'year': row[1],'month':row[2], 'consumed_power_sum': row[3], 'excess_power_sum': row[4]} for row in result]
    print(data[0]['excess_power_sum'], file=sys.stderr)
    # Return the data as JSON
    return jsonify(data)

# Render Monthly javascript and return rendered html
@app.route('/renMonthly')
def renMonthly():
    return render_template("monthly.html")
#---------    Monthly flask End     ----------#


########## Route to add device for logged in user to the db #######

""" @app.route('/addDevice')
def addDevice():
    return render_template("AddDevice.html")

@app.route('/add_device', methods=['POST'])
def add_device():
    # Get the current user ID from the session
    user_id = current_user

    # Get the device information from the form
    device_id = request.form['device_id']
    device_name = request.form['device_name']

    # Add the device to the database
    db.add_device(user_id, device_id, device_name)



    # Redirect the user to a page that displays their devices
    return redirect(url_for('devices')) """


@app.route('/addDevice', methods=['GET', 'POST'])
def add_device():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    # If the form was submitted, add the device to the user's account
    if request.method == 'POST':
        device_name = request.form['device_name']
        #device_type = request.form['device_type']
        user_id = current_user.id

        # Insert the new device into the database
        cursor = cnx.cursor()
        query = "INSERT INTO device (serial, user_id) VALUES (%s, %s)"
        cursor.execute(query, (device_name, user_id))
        cnx.commit()

    # Get a list of the user's devices from the database
    cursor = cnx.cursor()
    query = "SELECT serial, id FROM device WHERE user_id = %s"
    cursor.execute(query, (current_user.id,))
    devices = [{'device_name': row[0], 'device_id': row[1]} for row in cursor.fetchall()]

    # Render the devices.html template, passing in the list of devices
    return render_template('AddDevice.html', devices=devices)


#-------- Route add device end ----------
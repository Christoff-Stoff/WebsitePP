from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask import render_template, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User,Device,Hourly_Summary,Daily_Summary,Monthly_Summary,Device_Data
from werkzeug.urls import url_parse


from flask import Flask, request, jsonify
import mysql.connector
#Debug using:
#print(ValueToPrint, file=sys.stderr)

import sys,os

defaultDate="2021-01-01"
devName= None
#This can and probably should be changed to /Home, but keep @app.route('/') to display home page when no route is entered or directed to
@app.route('/')
@app.route('/index')
@login_required
def index():

    return render_template("index.html", title='Home Page')


#Login route, verifies if the usrer isn't already logged in or if the correct information is supplied
@app.route('/login', methods=['GET', 'POST'])
def login():
    users = db.session.query(User).all()
    Devicess = db.session.query(Device).all()
    print(Devicess,file = sys.stderr)
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




#Logs the user out
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('Home'))

#Route to register user, if requirements are met user is created and added to the db, then user is redirected to login page
@app.route('/register', methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('Home'))
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
    

    # Get a list of the user's devices from the database and device to session
    selected_date = request.form.get('selected-date')
    session['selected_date'] = selected_date
    
    selected_device = request.form.get('device_name')
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

    # How the qeurie would look for SQLAlchemy
    """ results = db.session.query(HourlySummary.generated_power, HourlySummary.date, HourlySummary.consumed_power, HourlySummary.excess_power)\
                    .join(Device, HourlySummary.device_id == Device.id)\
                    .filter(HourlySummary.date.between(start_date, end_date))\
                    .filter(Device.serial == device_serial)\
                    .all() """

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



    query = "SELECT generated_power_sum,DATE(date) AS date,consumed_power_sum,excess_power_sum FROM daily__summary ds JOIN device d ON ds.device_id = d.id WHERE MONTH(ds.date) = MONTH(%s) AND YEAR(ds.date) = YEAR(%s) AND d.serial = %s"
    cursor.execute(query, (selected_date,selected_date,device_name))
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

    # Return the data as JSON
    return jsonify(data)

# Render Monthly javascript and return rendered html
@app.route('/renMonthly')
def renMonthly():
    return render_template("monthly.html")
#---------    Monthly flask End     ----------#


########## Route to add device for logged in user to the db #######
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
        query = "INSERT INTO device (serial, user_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE user_id = %s"
        cursor.execute(query, (device_name, user_id, user_id))
        cnx.commit()

    # Get a list of the user's devices from the database
    cursor = cnx.cursor()
    query = "SELECT serial, id FROM device WHERE user_id = %s"
    cursor.execute(query, (current_user.id,))
    devices = [{'device_name': row[0], 'device_id': row[1]} for row in cursor.fetchall()]

    # Render the devices.html template, passing in the list of devices
    return render_template('AddDevice.html', devices=devices, title= "Devices")
#-------- Route add device end ------------------------------------



########## Route for contact page #######
@app.route('/contact')
def contact():
    return render_template("contact.html")
#-------- Route for contact page end -----



########## Route for Populating Daily Table #######
def populate_daily():

    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()
    # generate the daily summary for all devices
    cursor.execute("""INSERT INTO daily__summary (device_id, date, generated_power_sum, consumed_power_sum, excess_power_sum, savings_sum)
                    SELECT device_id, DATE(date), SUM(generated_power), SUM(consumed_power), SUM(excess_power), SUM(savings)
                    FROM hourly__summary AS h
                    GROUP BY device_id, DATE(h.date)
                    ON DUPLICATE KEY UPDATE
                    generated_power_sum = VALUES(generated_power_sum),
                    consumed_power_sum = VALUES(consumed_power_sum),
                    excess_power_sum = VALUES(excess_power_sum),
                    savings_sum = VALUES(savings_sum);""")
    cnx.commit()

#-------- Route for Populating Daily Table ---------



########## Route for Populating Monthly Table #######
def populate_monthly():

    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    # generate the monthly summary for all devices
    cursor.execute("""INSERT INTO monthly__summary (device_id, year, month, generated_power_sum, consumed_power_sum, excess_power_sum, savings_sum)
        SELECT device_id,
            YEAR(date) AS year,
            MONTH(date) AS month,
            SUM(generated_power_sum) AS generated_power_sum,
            SUM(consumed_power_sum) AS consumed_power_sum,
            SUM(excess_power_sum) AS excess_power_sum,
            SUM(savings_sum) AS savings_sum

            FROM daily__summary
            GROUP BY device_id, year(date), month(date)
            ON DUPLICATE KEY UPDATE
            generated_power_sum = VALUES(generated_power_sum),
            consumed_power_sum = VALUES(consumed_power_sum),
            excess_power_sum = VALUES(excess_power_sum),
            savings_sum = VALUES(savings_sum);
            """)
    cnx.commit()
#-------- Route for Populating Monthly Table --------



########## Route for Populating Yearly Table #######
def populate_yearly():

    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()


    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    # generate the monthly summary for all devices
    cursor.execute("""INSERT INTO yearly__summary (device_id, year, generated_power_sum, consumed_power_sum, excess_power_sum, savings_sum)
                    SELECT device_id, year, SUM(generated_power_sum) AS generated_power_sum,
                        SUM(consumed_power_sum) AS consumed_power_sum, SUM(excess_power_sum) AS excess_power_sum,
                        SUM(savings_sum) AS savings_sum
                    FROM monthly__summary
                    GROUP BY device_id, year
                    ON DUPLICATE KEY UPDATE
                    generated_power_sum = VALUES(generated_power_sum),
                    consumed_power_sum = VALUES(consumed_power_sum),
                    excess_power_sum = VALUES(excess_power_sum),
                    savings_sum = VALUES(savings_sum);""")
    cnx.commit()
#-------- Route for Populating Yearly Table --------



########### Populate hourly table using Device Data ########
def populate_hourly_table():

    devices = Device.query.all()
    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    for device in devices:
        device_data = Device_Data.query.filter(Device_Data.device_serial == device.serial).all()
        #print(device_data)
        for data in device_data:
            
            date = (data.timestamp)
            generated_power= data.generated_power
            consumed_power= (data.consumed_power)
            excess_power= data.excess_power
            savings= data.savings
            hourlySummary = Hourly_Summary( device_id = device.id,
                                            date = date,
                                            generated_power=generated_power,
                                            consumed_power=consumed_power,
                                            excess_power = excess_power,
                                            savings= savings)
            
            #Duplication prevention
            cursor.execute(""" INSERT INTO hourly__summary(device_id, date, generated_power, consumed_power, excess_power, savings)
            VALUES (%s, %s, %s, %s, %s, %s)
            GROUP BY device_id, date
            ON DUPLICATE KEY UPDATE
            generated_power = VALUES(generated_power),
            consumed_power = VALUES(consumed_power),
            excess_power = VALUES(excess_power),
            savings = VALUES(savings);""", (hourlySummary.device_id, hourlySummary.date, hourlySummary.generated_power, hourlySummary.consumed_power, hourlySummary.excess_power, hourlySummary.savings))

            cnx.commit()
            #db.session.merge(hourlySummary)
#----------- Populate hourly table using Device Data ------




########### Import Excel and Populate Device Data ########
import pandas as pd
from datetime import datetime
import openpyxl
#Read excel file
def ReadExcel():
    file_path = os.path.abspath("app/data.xlsx")

    df = pd.read_excel(file_path, sheet_name='Sheet1')
    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()
    #Iterate over each row in the file
    for index, row in df.iterrows():
        # Check if the device already exists
        device = Device.query.filter_by(serial =row['serial']).first()
        if not device:
            # Create a new device
            device = Device(serial=row['serial'])
            db.session.add(device)

        # Create a new device data object
        date = row['date']           
        generated_power= row['generated_power']
        consumed_power= row['consumed_power']
        excess_power= row['excess_power']
        savings= row['savings']
        hourlySummary = Hourly_Summary( device_id = device.id,
                                        date = date,
                                        generated_power=generated_power,
                                        consumed_power=consumed_power,
                                        excess_power = excess_power,
                                        savings= savings)
        
        #Duplication prevention
        cursor.execute(""" INSERT INTO hourly__summary(device_id, date, generated_power, consumed_power, excess_power, savings)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        generated_power = VALUES(generated_power),
        consumed_power = VALUES(consumed_power),
        excess_power = VALUES(excess_power),
        savings = VALUES(savings);""", (hourlySummary.device_id, hourlySummary.date, hourlySummary.generated_power, hourlySummary.consumed_power, hourlySummary.excess_power, hourlySummary.savings))

        
    # Commit changes
    cnx.commit()
#----------- Import Excel and Populate Device Data --------


############ Route to populate DB using Excel ###########
@app.route('/ExcelPop')
def ExcelPop():
    ReadExcel()
    #populate_hourly_table()

    return "Population Complete"
#----------- Route to populate DB using Excel -----------

@app.route('/PopSum')
def PopSum():
    populate_daily()
    populate_monthly()
    populate_yearly()
    return "Summary Population Complete"

@app.route('/ClearDB')
def ClearDB():
    # Connect to database server
    cnx = mysql.connector.connect(user=username, password=password,
                                  host=servername, database=dbname)
    cursor = cnx.cursor()

    # generate the monthly summary for all devices
    cursor.execute(""" DELETE FROM hourly__summary """)
    cursor.execute(""" DELETE FROM daily__summary """)
    cursor.execute(""" DELETE FROM monthly__summary """)
    cursor.execute(""" DELETE FROM yearly__summary """)

    cnx.commit()

    return "Summaries Cleared"
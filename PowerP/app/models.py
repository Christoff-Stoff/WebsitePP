from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

#User database model
class User(UserMixin, db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(64),index = True, unique=False)
    email = db.Column(db.String(120), index =True, unique=True)
    password_hash=db.Column(db.String(128))
    devices = db.relationship('Device', backref='owner', lazy='dynamic')

#Note the password is hashed before it is stored in the database, and reverse hashing is used in order to check the password. Thus even if the database values are obtained the password will still be secured.
    #create a hashed password
    def set_password(self, password):
        self.password_hash=generate_password_hash(password)

    #Validate if the supplied password is correct
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return '<User {}>'.format(self.username)

#The database model for a device which is linked to a user (device.owner will return the user that is linked to the device)
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.String(120), index=True, unique=True) #Device Serial number, NOTE: Serial number is unique, this is how we track and link data to the device
    #Device_Location = db.Column(db.String(140)) -> Add and update the db if the implementation of giving live weather wants to be added
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    #Below we define the realationship to the device and the summaries.
    #The reason for this is we can create a Device object and can easily retrieve the summaries by just calling objectName.hourly_summaries.all()
    data = db.relationship('Device_Data', backref= 'device', lazy='dynamic')
    hourly_summaries = db.relationship('Hourly_Summary', backref='device', lazy='dynamic')
    daily_summaries = db.relationship('Daily_Summary', backref='device', lazy='dynamic')
    monthly_summaries = db.relationship('Monthly_Summary', backref='device', lazy='dynamic')
    yearly_summaries = db.relationship('Yearly_Summary', backref='device', lazy='dynamic')

    def __repr__(self): # For debugging purposes, will return <Device "Device_Name">
        return '<Device {}>'.format(self.Device_Name)


#The data that is pulled for a device
class Device_Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, index=True)
    generated_power= db.Column(db.Float)
    consumed_power= db.Column(db.Float)
    device_id= db.Column(db.Integer, db.ForeignKey('device.id'))
    #unit_cost = db.Column(db.Float)  -> How much it cost per kWh unit electricity, thus we calaculate the savings for that device


# Uses Devices data table and puts values into an hourly sum
class Hourly_Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True)
    generated_power= db.Column(db.Float)
    consumed_power= db.Column(db.Float)
    excess_power= db.Column(db.Float)
    savings = db.Column(db.Float)
    device_id= db.Column(db.Integer, db.ForeignKey('device.id'))


#Links to Hourly summary in order to be able to display entire day's data
#Also includes the sum total values for entire day
class Daily_Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True)
    generated_power_sum= db.Column(db.Float)
    consumed_power_sum= db.Column(db.Float)
    excess_power_sum= db.Column(db.Float)
    savings_sum = db.Column(db.Float)
    device_id= db.Column(db.Integer, db.ForeignKey('device.id'))


#Links to Daily summary in order to be able to display entire month's data
#Also includes the sum total values for month day
class Monthly_Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    month = db.Column(db.Integer, index=True)
    year = db.Column(db.Integer, index=True)
    generated_power_sum= db.Column(db.Float)
    consumed_power_sum= db.Column(db.Float)
    excess_power_sum= db.Column(db.Float)
    savings_sum = db.Column(db.Float)
    device_id= db.Column(db.Integer, db.ForeignKey('device.id'))


#Links to monthly summary in order to be able to display entire year's data
#Also includes the sum total values for entire month
class Yearly_Summary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    generated_power_sum= db.Column(db.Float)
    consumed_power_sum= db.Column(db.Float)
    excess_power_sum= db.Column(db.Float)
    savings_sum = db.Column(db.Float)
    device_id= db.Column(db.Integer, db.ForeignKey('device.id'))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
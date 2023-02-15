from app import app, db
from app.forms import LoginForm, RegistrationForm
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user,login_required
from app.models import User
from werkzeug.urls import url_parse

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
from picamera import PiCamera
from cardstunt_opencv import *
import RPi.GPIO as GPIO
import time
import os
import urllib.request
import cv2 as cv
import numpy as np
import math
from werkzeug.utils import secure_filename
from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash
)

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

# set allowed users
users = []
users.append(User(id=1, username='Jirajet', password='Ton'))
users.append(User(id=2, username='Pantapat', password='Pau'))
users.append(User(id=3, username='Thanasit', password='Max'))

app = Flask(__name__, template_folder='template')
app.secret_key = 'somesecretkeythatonlyishouldknow'

# check user id
@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

# login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']

        user = [x for x in users if x.username == username][0]
        if user and user.password == password:
            session['user_id'] = user.id
            return redirect(url_for('profile'))

        return redirect(url_for('login'))

    return render_template('login.html')

# action page
@app.route('/profile', methods=["GET", "POST"])
def profile():
    if not g.user:
         return redirect(url_for('login'))
    if request.method == 'POST':
        if request.form.get('action1') == 'Capture Photo':
            capture_photo() 
        elif request.form.get('action2') == 'Show':
            show()
        elif request.form.get('action3') == 'Unshow':
            unshow()

    return render_template('profile.html')

# run the web app
app.debug = True
app.run()
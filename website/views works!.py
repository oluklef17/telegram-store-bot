from platform import platform
from cryptography.fernet import Fernet
from datetime import datetime
from flask import Blueprint, render_template, request, flash, jsonify, send_file
from flask_login import login_required, current_user
from . import db
from .models import User
from sqlalchemy.orm import sessionmaker
import random
import json
import requests
import threading
from pathlib import Path
import os
import sys


Session = sessionmaker(bind=db.engine)
session = Session()

last_msg = ''
views = Blueprint('views', __name__)

botAPI = '5686900763:AAGCVu_1-gPql9Rsnc8sydnbNmVZ5xosdNg' #5686900763:AAGCVu_1-gPql9Rsnc8sydnbNmVZ5xosdNg

url = f'https://api.telegram.org/bot{botAPI}/getUpdates'
resp = requests.get(url).json()['result']
offset = '900008932' #resp[-1]['update_id']
read = list()


@views.route('/', methods=['GET', 'POST'])
#@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/createuser', methods=['GET', 'POST'])
def createuser():
    if request.method == 'POST':
        key = Fernet.generate_key()
        f = Fernet(key)
        email     = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        enc_email = email.encode()
        lic_key   = str(f.encrypt(enc_email))
        terminals = request.form.get('terminals')
        exp_date  = datetime.strptime(request.form.get('expiry'),'%Y-%m-%d')
        if user:
            if len(terminals) > 0:
             user.terminals = terminals
            if len(request.form.get('expiry')) > 0:
             user.exp_date  = exp_date
            return render_template("home.html")
        else:
            new_user = User(email=email, lic_key=lic_key, terminals=terminals, terms_in_use=0, exp_date=exp_date)
            db.session.add(new_user)
            db.session.commit()
            name = email[:email.find('@')]
            with open('licenses\\'+name+'.lic', 'w') as f:
                f.write(lic_key)
            home = os.path.abspath(os.curdir)
            path = os.path.join(home,'licenses\\'+name+'.lic')
            return send_file(path, as_attachment=True)
    return render_template("home.html")

@views.route('/editpage', methods=['GET', 'POST'])
def editpage():
    return render_template("edit.html")

@views.route('/edituser', methods=['GET', 'POST'])
def edituser():
    email     = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    terminals = request.form.get('terminals')
    exp_date  = datetime.strptime(request.form.get('expiry'),'%Y-%m-%d')
    if user:
     if len(terminals) > 0:
      user.terminals = terminals
     if len(request.form.get('expiry')) > 0:
      user.exp_date  = exp_date
     db.session.commit()
     return render_template("home.html")
    else:
     print('User does not exist.')
     return render_template("home.html")


@views.route('/removepage', methods=['GET', 'POST'])
def removepage():
    return render_template("delete.html")

@views.route('/removeuser', methods=['GET', 'POST'])
def removeuser():
    email     = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    if user:
     db.session.delete(user)
     db.session.commit()
     return render_template("home.html")
    else:
     print('User does not exist.')
     return render_template("home.html")

@views.route('/checklicense/<code>', methods=['GET', 'POST'])
def checklicense(code):
    user = User.query.filter_by(lic_key=code).first()
    if user:
        return 'Verification successful'
    else:
        return 'Invalid license code'

@views.route('/checkexpiry/<code>', methods=['GET', 'POST'])
def checkexpiry(code):
    user = User.query.filter_by(lic_key=code).first()
    if user:
        currentTime = datetime.now()
        expiryDate  = user.exp_date
        db.session.delete(user)
        db.session.commit()
        if currentTime > expiryDate:
         return 'License has expired'
        else:
         return 'License valid till '+str(expiryDate)
    else:
        return 'Invalid license code'

@views.route('/addterminal/<code>', methods=['GET', 'POST'])
def addterminal(code):
    user = User.query.filter_by(lic_key=code).first()
    if user.terms_in_use < int(user.terminals):
     user.terms_in_use += 1
     db.session.commit()
     return 'New terminal added'
    else:
     return 'Max number of terminals added'

@views.route('/removeterminal/<code>', methods=['GET', 'POST'])
def removeterminal(code):
    user = User.query.filter_by(lic_key=code).first()
    if user.terms_in_use > 0:
     user.terms_in_use -= 1
     db.session.commit()
     return 'Terminal removed'
    else:
     return 'No terminals to remove'


    



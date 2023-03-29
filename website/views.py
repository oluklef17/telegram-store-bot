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
import random


Session = sessionmaker(bind=db.engine)
session = Session()

last_msg = ''
views = Blueprint('views', __name__)

botAPI = '5007154718:AAHWEu2vCue-1hPS1iZqbWasSg5fywVvjB0' #5686900763:AAGCVu_1-gPql9Rsnc8sydnbNmVZ5xosdNg

url = f'https://api.telegram.org/bot{botAPI}/getUpdates'
resp = requests.get(url).json()['result']
offset = '0' #resp[-1]['update_id']
read = list()


@views.route('/', methods=['GET', 'POST'])
#@login_required
def home():
    return render_template("auth.html")

@views.route('/adminauth', methods=['GET', 'POST'])
#@login_required
def adminauth():
    if request.method == 'POST':
        username     = request.form.get('username')
        password     = request.form.get('password')
        if username  == 'maridasan' and password == 'April#22':
          flash('Logged in successfully!', category='success')
          return render_template("home.html")
        else:
          flash('Logged in successfully!', category='success')
          return render_template("auth.html")

@views.route('/logout', methods=['GET', 'POST'])
#@login_required
def logout():
    return render_template("auth.html")

@views.route('/createuser', methods=['GET', 'POST'])
def createuser():
    if request.method == 'POST':
        part1 = random.randint(1000,9999)
        part2 = random.randint(1000,9999)
        part3 = random.randint(1000,9999)
        part4 = random.randint(1000,9999)
        key = Fernet.generate_key()
        f = Fernet(key)
        email     = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        enc_email = email.encode()
        lic_key   = str(part1) + '-' + str(part2) + '-' + str(part3) + '-' + str(part4)
        print('Licence key is ',lic_key)
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

@views.route('/getsignal', methods=['GET', 'POST'])
def getsignal():
    signal = get_lastmessage()
    return str(signal)

def get_lastmessage():
    try:
        global offset
        url = f'https://api.telegram.org/bot{botAPI}/getUpdates?offset={offset}'
        response = requests.get(url)
        resp = response.json()['result']
        #send_url = 'https://api.telegram.org/bot5007154718:AAHWEu2vCue-1hPS1iZqbWasSg5fywVvjB0/sendMessage?chat_id=1380098782&text=New message received'
        #sent = requests.get(send_url)
        last_msg = ''
        if 'channel_post' in resp[-1]:
         last_msg = resp[-1]['channel_post']['text']
        elif 'edited_channel_post' in resp[-1]:
         last_msg = resp[-1]['edited_channel_post']['text']
        offset = resp[-1]['update_id']
        LM = last_msg.upper()
        is_entry = LM.find('SL') != -1 and LM.find('TP') != -1 and (LM.find('BUY') != -1 or LM.find('SELL') != -1)
        replied = ''
        msg_id = ''
        if 'channel_post' in resp[-1]:
            if 'reply_to_message' in resp[-1]['channel_post'] and is_entry==False:
                last_msg = resp[-1]['channel_post']['text']
                replied = resp[-1]['channel_post']['reply_to_message']['text']
                msg_id = resp[-1]['channel_post']['reply_to_message']['message_id']
                print("Message ID is ",msg_id)
        elif 'edited_channel_post' in resp[-1]:
            if 'reply_to_message' in resp[-1]['edited_channel_post'] and is_entry==False:
                last_msg = resp[-1]['edited_channel_post']['text']
                replied = resp[-1]['edited_channel_post']['reply_to_message']['text']
                msg_id = resp[-1]['edited_channel_post']['reply_to_message']['message_id']
        if str(response).find('200') == -1:
            return('FAILED TO GET RESPONSE.')
        else:
            if replied == '':
             return('Telecopierz\n'+last_msg+' {'+str(msg_id)+'}')
             #print('Adivah Trade Ideas ??\n'+last_msg)
            else:
             return('Telecopierz\n'+replied+'|'+last_msg+' {'+str(msg_id)+'}')
             #print('Adivah Trade Ideas ??\n'+replied+'|'+last_msg)
    except Exception as e:
        return('Failed to get last message due to error ',e)


@views.route('/getlogo', methods=['GET', 'POST'])
def getlogo():
    path = 'telecopierz.bmp'
    return send_file(path, as_attachment=True)




    



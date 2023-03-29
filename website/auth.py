from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import os
from telethon.sync import TelegramClient, events, functions, types

api_id   = 19533412
api_hash = '244adfc8d6a54f85df6958ac3823e203'



auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.manual'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/verify/<details>', methods=['GET', 'POST'])
def verify(details):
    if request.method == 'GET':
        parts = details.split(',')
        if len(parts)==0:
            return 'Invalid arguments received.'
        email = parts[0]
        password = parts[1]
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                name = email[:email.find('@')]
                parentDirectory = os.getcwd()
                if os.path.exists(f'website/sessions/{name}.txt') == False:
                    with open(f'website/sessions/{name}.txt', 'w', encoding='utf8') as f:
                        f.write(details)
                    return 'Verification successful.'
                else:
                    content = ''
                    with open(f'website/sessions/{name}.txt', 'r', encoding='utf8') as f:
                        content = f.read()
                        if details != content:
                          return 'You have already attached a terminal.'
                        else:
                          return 'Verification successful.'
            else:
                return 'Incorrect password, try again.'
        else:
            return 'Email does not exist.'

@auth.route('/endsession/<details>', methods=['GET', 'POST'])
def endsession(details):
    if request.method == 'GET':
        parts = details.split(',')
        if len(parts)==0:
            return 'Invalid arguments received.'
        email = parts[0]
        password = parts[1]
        user = User.query.filter_by(email=email).first()
        if user:
            name = email[:email.find('@')]
            parentDirectory = os.getcwd()
            if os.path.exists(f'website/sessions/{name}.txt') == True:
                os.remove(f'website/sessions/{name}.txt')
                return 'Session ended.'
            else:
                return 'Incorrect password, try again.'
        else:
            return 'Email does not exist.'


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, password=generate_password_hash(
                password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

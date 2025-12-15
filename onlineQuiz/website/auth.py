from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash # une function hash pour securiser les mot de passes
from . import db

from flask_login import login_user, login_required, logout_user, current_user



auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash ('Logged in successfully!', category='success')
                login_user(user, remember=True) 
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
        
        # Safe print with encoding
        try:
            print(f"FORM DATA - Email: {email}, Password: {password}    ")
        except Exception as e:
            current_app.logger.error(f"Print failed: {e}")
        
    return render_template('login.html', user=current_user)

@auth.route('/logout')

@login_required # assure que l'utilisateur est connecté avant de lui permettre de se déconnecter
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')

        # Form data validation (PROPERLY INDENTED)
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(firstName) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else: 
            new_user = User(email=email, first_name=firstName, password=generate_password_hash(password1))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created!', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.home'))


    
    return render_template('sign_up.html' , user=current_user)



   
   
   
   
   
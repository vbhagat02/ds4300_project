from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from db_utils import get_user, insert_listing, insert_user
from __init__ import User, Listing

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listings.html'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        u = get_user(email)
        if u:
            if check_password_hash(u[5], password):
                flash('Logged in Successfully', category='success')
                user = User(u[0], u[1], u[2], u[3], u[4], u[5], u[6],
                            u[7], u[8], u[9], u[10], u[11], u[12], u[13], u[14])
                login_user(user)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template('login.html', user=current_user)


@auth.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))


@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        dob = request.form.get('dob')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user_by_email = get_user(email)
        if user_by_email:
            flash('A user with this email already exists.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            insert_user(name, email, dob, username,
                        generate_password_hash(password1, method='sha256'))
            u = get_user(email)
            user = User(u["name"], u["email"], u["dob"],
                        u["username"], u["password"])
            login_user(user)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)


@auth.route('/listings', methods=['GET', 'POST'])
def create_listing():
    if request.method == 'POST':
        # get all the responses from the user
        uid = request.form.get('userid')
        street = request.form.get('street')
        city = request.form.get('city')
        state = request.form.get('state')
        zipcode = request.form.get('zipcode')
        bed = request.form.get('bedrooms')
        bath = request.form.get('bathrooms')
        rent = request.form.get('rent')

        insert_listing(uid, street, city, state, zipcode, bed, bath, rent)
        flash('Listing created!', category='success')
        return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)

from flask import Blueprint, render_template, request, redirect, flash
from flask.helpers import url_for
from flask_login import login_required, current_user
from flask_login.utils import logout_user
from . import UPLOAD_FOLDER, db, delete_user, get_user_photo, get_user_address, app, update_user_bio, update_user_phone, update_user_city, update_user_country, update_user_state
from .auth import allowed_file
from werkzeug.utils import secure_filename
import os
import pathlib

views = Blueprint('views', __name__)


@views.route("/", methods=['GET', 'POST'])
@login_required
def home():
    return render_template("login_page.html", user=current_user)


@views.route("/signup", methods=['GET', 'POST'])
@login_required
def profile():

    return render_template("sign_up.html", user=current_user)


@views.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():

    return render_template("user_profile.html", user=current_user)


@views.route("/listings", methods=['GET', 'POST'])
@login_required
def profile():

    return render_template("listings.html", user=current_user)

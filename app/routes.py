# app/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User, StudyEntry
from .extensions import db
from .forms import RegisterForm, LoginForm, UploadForm

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('base.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists")
            return redirect(url_for('main.register'))

        hashed_pw = generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully! Please log in.")
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Logged in successfully!")
            return redirect(url_for('main.home'))
        else:
            flash("Invalid username or password.")
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('main.login'))

@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        entry = StudyEntry(
            user_id=current_user.id,
            unit=form.unit.data,
            hours=form.hours.data,
            date=form.date.data,
            mood=form.mood.data
        )
        db.session.add(entry)
        db.session.commit()
        flash('Study entry added successfully!')
        return redirect(url_for('main.home'))
    return render_template('upload.html', form=form)

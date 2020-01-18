import os

from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'changeme')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    favorites = db.relationship('Favorite', backref='user', lazy=True)


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    picture_url = db.Column(db.Text)
    quote = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


def get_cat_picture():
    # Random cat pictures
    url = 'https://api.thecatapi.com/v1/images/search?limit=1&order=Random&mime_types=jpg'
    cat_api_response = requests.get(url).json()
    return cat_api_response[0]['url']


def get_quote():
    # Random math quotes
    url = 'https://random-math-quote-api.herokuapp.com/'
    quote_api_response = requests.get(url).json()
    return f'{quote_api_response["quote"]} - {quote_api_response["author"]}'


@app.route('/')
def index():
    return render_template('index.html', url=get_cat_picture(), quote=get_quote())


@app.route('/save-favorite', methods=['POST'])
def save_favorite():
    user = User.query.filter_by(username=session.get('username')).first()
    url = request.form.get('url')
    quote = request.form.get('quote')
    if user and url and quote:
        favorite = Favorite(picture_url=url, quote=quote, user_id=user.id)
        db.session.add(favorite)
        db.session.commit()
    return redirect('/')


@app.route('/favorites')
def get_favorites():
    favorites = []
    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    if user:
        favorites = user.favorites
    return render_template('favorites.html', favorites=favorites)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('You do not have an account. Please register one.')
            return redirect(url_for('register'))
        if not check_password_hash(user.password, password):
            flash('Incorrect password, try again.')
            return redirect(url_for('login'))
        session['username'] = user.username
        return redirect(url_for('index'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # TODO: Add email and require confirmation before creating a new account
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_doesnt_exist = User.query.filter_by(username=username).first() is None
        if username and password and user_doesnt_exist:
            user = User(username=username, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash(f'The username {username} is not available, please choose another')
            return redirect(url_for('register'))
    else:
        return render_template('register.html')

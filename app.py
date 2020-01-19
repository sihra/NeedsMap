import os

from flask import Flask, render_template, request, redirect, session, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
# Flask Google Maps
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map

from flask_sqlalchemy import SQLAlchemy

import requests

app = Flask(__name__, template_folder="templates")
app.secret_key = os.getenv('SECRET_KEY', 'changeme')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class needsmap(db.Model):
    address_id = db.Column(db.String(300), nullable=False)
    username = db.Column(db.String(80), unique=True,primary_key=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    longitude = db.Column(db.Float(40))
    latitude = db.Column(db.Float(40))
    
    food = db.Column(db.Integer())
    clothing = db.Column(db.Integer())
    femprod = db.Column(db.Integer())
    toilet = db.Column(db.Integer())
    shoes=db.Column(db.Integer())
    cash=db.Column(db.Integer())

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     pwd = db.Column(db.String(80), nullable=False)
#     favorites = db.relationship('Favorite', backref='user', lazy=True)


# class Favorite(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     picture_url = db.Column(db.Text)
#     quote = db.Column(db.Text)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def get_coordinates(location_detail):
    # encodeURIComponent()
    url= "https://maps.googleapis.com/maps/api/geocode/json?address="+location_detail["address"]+"&key=AIzaSyDPQ4t0bcLgc1FByDOrjDZxjQL_yoEly4I"
    response = requests.get(url).json()
    print(response)
    return (response['results'][0]['geometry']['location']['lat'], response['results'][0]['geometry']['location']['lng'])
    
    
# def get_cat_picture():
#     # Random cat pictures
#     url = 'https://api.thecatapi.com/v1/images/search?limit=1&order=Random&mime_types=jpg'
#     cat_api_response = requests.get(url).json()
#     return cat_api_response[0]['url']


# def get_quote():
#     # Random math quotes
#     url = 'https://random-math-quote-api.herokuapp.com/'
#     quote_api_response = requests.get(url).json()
#     return f'{quote_api_response["quote"]} - {quote_api_response["author"]}'


# @app.route('/')
# def index():
#     return render_template('index.html', url=get_cat_picture(), quote=get_quote())

@app.route('/form',methods=['GET','POST'])
def form():
    if request.method == 'POST':
        # name= request.form.get('name')
        # if name == None:
        #     flash('Name field is empty! Please provide a valid shelter name')
        # else:
        #     #check if shelter manager has access to this shelter 
        # location = request.form.get('location')
        # if location == None:
        #     flash('Location field is empty! Please provide a valid shelter location') 
        # else:
        #     #check if shelter manager has access to this location  
        
        resource=request.form.get('resource')
        if resource == "--None--" :
           flash('Please select a valid resource!')
           return redirect(url_for('form'))
        
            
        alert_number =request.form.get('alert')
        if alert_number == "--None--":
           flash('Please select a valid priority number!')
           return redirect(url_for('form'))
        else:
            username = session.get('username')
            user = needsmap.query.filter_by(username=username).first()
            user.resource = int(alert_number)
            db.session.commit()
        
        flash("You have successfully submitted the details! Please logout if you don't have any more updates or you can continue updating the form")
        return redirect(url_for('form'))

    else:
        # def dropdown():
            #fetch name from db and store it in name
        name=session.get('username')
        user = needsmap.query.filter_by(username=name).first()

            #fetch location from db and store it in location
        
        location = user.address_id
        resources = ['--None--','Food', 'Toiletries', 'Clothes', 'Shoes','Feminine Supplies','Monetary Donations']
        alerts = ['--None--','0','1','2','3','4']
        return render_template('form.html', name = name,location = location,resources=resources,alerts = alerts)
        

# @app.route('/save-favorite', methods=['POST'])
# def save_favorite():
#     user = User.query.filter_by(username=session.get('username')).first()
#     url = request.form.get('url')
#     quote = request.form.get('quote')
#     if user and url and quote:
#         favorite = Favorite(picture_url=url, quote=quote, user_id=user.id)
#         db.session.add(favorite)
#         db.session.commit()
#     return redirect('/')


# @app.route('/favorites')
# def get_favorites():
#     favorites = []
#     username = session.get('username')
#     user = User.query.filter_by(username=username).first()
#     if user:
#         favorites = user.favorites
#     return render_template('favorites.html', favorites=favorites)

@app.route('/gotologin')
def gotologin():
    return render_template('login.html')

@app.route('/gotoregister')
def gotoregister():
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        username = request.form.get('username')
        user = needsmap.query.filter_by(username=username).first()
        if user is None:
            flash('You do not have an account. Please register one.')
            return redirect(url_for('register'))
        if not check_password_hash(user.password, password):
            flash('Incorrect password, try again.')
            return redirect(url_for('login'))
        session['username'] = user.username
        return redirect(url_for('form'))
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
        location = request.form.get('location')
       
        name = request.form.get('name')

        user_doesnt_exist = needsmap.query.filter_by(username=username).first() is None
        
        if username and password and location and name and user_doesnt_exist:
            # location = location.strip()
            location_detail = {'address':location}
            (lat,lng)=get_coordinates(location_detail)
            user = needsmap(username=username, password=generate_password_hash(password),address_id= location,name=name,latitude=float(lat),longitude=float(lng))
            db.session.add(user)
            db.session.commit()

            return redirect(url_for('login'))
        else:
            flash(f'The username {username} is not available, please choose another')
            return redirect(url_for('register'))
    else:
        return render_template('register.html')


#API Key Initialization

app.config['GOOGLEMAPS_KEY'] = "AIzaSyDPQ4t0bcLgc1FByDOrjDZxjQL_yoEly4I"

# Initialize the extension
GoogleMaps(app)

#def setMarkers(map):

@app.route('/')
def index():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=34.0522,
        lng=-118.2437,
        style="height:600px;width:75%;margin:0;",
        #Call function to generate markers
       # markers=[]
    ) 
    #fromsetMarkers(mymap)


    # adding markers to map from database
    #def addmarker():
    	#marker={
    		#if need value is '1', set icon to yellow-dot e.g. icons.dots.yellow: [(x,y)]
    		#if need value is '2', set icon to orange-dot
    		#if need value is '3', set icon to red-dot

    		#translate address into lat & lng

    		#set the infobox to: 
    		#name of shelter (possibly with link to their website OR a link to our page )
    		#address
    		#what they need


    	#}
    	#marker.setMap(mymap)
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('index.html', mymap=mymap)
if __name__ == "__main__":
    app.run(debug=True)

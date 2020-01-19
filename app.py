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



def get_coordinates(location_detail):
   
    url= "https://maps.googleapis.com/maps/api/geocode/json?address="+location_detail["address"]+"&key=AIzaSyDPQ4t0bcLgc1FByDOrjDZxjQL_yoEly4I"
    response = requests.get(url).json()
    print(response)
    return (response['results'][0]['geometry']['location']['lat'], response['results'][0]['geometry']['location']['lng'])
    
    

@app.route('/form',methods=['GET','POST'])
def form():
    if request.method == 'POST':
       
        resource=request.form.get('resource')
        if resource == "--None--" :
           flash('Please select a valid resource!')
           return redirect(url_for('form'))
        
            
        alert_number =request.form.get('alert')
        if alert_number == "--None--":
           flash('Please select a valid priority number!')
           return redirect(url_for('form'))
        else:
            username1 = session.get('username')
            user = needsmap.query.filter_by(username=username1).first()
            flash('hiiiii' + resource)
            if resource == "Food":
                user.food = int(alert_number)
                flash(user.food)
            elif resource == "Toiletries":
                user.toilet = int(alert_number)
            elif resource == "Clothes":
                user.clothing = int(alert_number)
            elif resource == "Shoes":
                user.shoes = int(alert_number)
            elif resource == "Feminine Supplies":
                user.femprod = int(alert_number)
                flash(user.femprod)
            elif resource == "Monetary Donations":
                user.cash = int(alert_number)
                flash(user.cash)
            db.session.commit()
        
        flash("You have successfully submitted the details! Please logout if you don't have any more updates or you can continue updating the form")
        return redirect(url_for('form'))

    else:
       
            #fetch name from db and store it in name
        name=session.get('username')
        user = needsmap.query.filter_by(username=name).first()

            #fetch location from db and store it in location
        
        location = user.address_id
        resources = ['--None--','Food', 'Toiletries', 'Clothes', 'Shoes','Feminine Supplies','Monetary Donations']
        alerts = ['--None--','1','2','3']
        return render_template('form.html', name = name,location = location,resources=resources,alerts = alerts)
        


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
    return redirect(url_for('/'))


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

"""
------------------------------------------------------------------------------------------------------------------------------------------------------------------------
"""


#API Key Initialization

app.config['GOOGLEMAPS_KEY'] = "AIzaSyDPQ4t0bcLgc1FByDOrjDZxjQL_yoEly4I"

# Initialize the extension
GoogleMaps(app)


#NeedsMapTable
def setMarkers():
    markers = []

    #table = needsmap.query.filter_by(needsmap.address_id!=null)
    rows = needsmap.query.all()


    for col in rows:
        mark = "<b>" + col.name +"</b> <p>"+col.address_id+ "</p><p>"

        food = chooseIcon(col.food)
        mark = mark + food+ " Food <br>"

        clothing = chooseIcon(col.clothing)
        mark = mark + clothing+ " Clothing <br>"

        femprod = chooseIcon(col.femprod)
        mark = mark + femprod+ " Feminine Products <br>"

        shoes = chooseIcon(col.shoes)
        mark = mark + shoes+ " Shoes <br>"

        toilet = chooseIcon(col.toilet)
        mark = mark + toilet + " Toiletries <br>"

        cash = chooseIcon(col.cash)
        mark = mark + cash+ " Cash <br></p>"

        m1 = {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': col.latitude,
             'lng': col.longitude,
             'infobox': mark
        }
        markers.append(m1)
    return markers


def chooseIcon(val):
    if(val == 1):
        return "🔴"
    elif(val == 2):
        return "🟡"
    else:
        return "🟢"

@app.route("/")
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=34.0522,
        lng=-118.2437,
        style="height:93.5vh;width:100%;margin-top:31px;",
        #Call function to generate markers
        markers=setMarkers()
    ) 
    return render_template('index.html', mymap=mymap)

    if __name__ == "__main__":
        app.run(debug=True)

    

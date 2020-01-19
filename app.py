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


#API Key Initialization

app.config['GOOGLEMAPS_KEY'] = "AIzaSyDPQ4t0bcLgc1FByDOrjDZxjQL_yoEly4I"

# Initialize the extension
GoogleMaps(app)


#def setMarkers(map):



@app.route("/")
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=34.0522,
        lng=-118.2437,
        style="height:600px;width:100%;margin:0;",
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

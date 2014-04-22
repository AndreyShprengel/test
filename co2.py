from flask import Flask, request, render_template
from sqlalchemy import func 
from sqlalchemy.sql import label
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pprint import pprint
from datetime import datetime, timedelta
from string import upper
from random import random, shuffle
from copy import deepcopy
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///co2.db'
db = SQLAlchemy(app, session_options = { 'expire_on_commit':False})


user = None
app.debug = True

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    name = db.Column(db.String)
    mpg = db.Column(db.String)
    
    def __init__(self, user_name, password, name, mpg):
        self.username = user_name
        self.password = password
        self.name = name
        self.mpg = mpg
    
class Trips(db.Model):
	
 
	id = db.Column(db.Integer, primary_key=True)
	points  = db.Column(db.Integer)
	date = db.Column(db.DateTime)
	
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user = db.relationship('Users',backref=db.backref('trips', lazy='dynamic'))
 
	def __init__(self, points, date, user):
		""""""

		self.points = points
		self.date = date
		self.user = user


@app.route('/')
@app.route("/home/")
def landing():
    global user
    return render_template('home.html', user = user)
@app.route('/echo/', methods = ['POST', 'GET'])
def echo():
    print "hello"
    
@app.route('/scores')
def scores():
    global user
    dailynames = []
    weeklynames = []
    monthlynames = []
    stuff = db.engine.execute("SELECT sum(points) points, user_id FROM  trips Where  date (date) between    date('now', '-7 days' ) and  date('now')  group by user_id order by points  DESC limit 5 ")
    for item in stuff:
		weeklynames.append(Users.query.filter_by( id = item.user_id).first().name)
    stuff = db.engine.execute("SELECT sum(points) points, user_id FROM  trips Where  date (date) between    date('now', '-7 days' ) and  date('now')  group by user_id order by points  DESC limit 5 ")
    weekres= zip(weeklynames,stuff)
    
    stuff = db.engine.execute("SELECT sum(points) points, user_id FROM  trips Where  date (date) between    date('now', '-1 days' ) and  date('now')  group by user_id order by points  DESC limit 5 ")
    for item in stuff:
		dailynames.append(Users.query.filter_by( id = item.user_id).first().name)
    stuff = db.engine.execute("SELECT sum(points) points, user_id FROM  trips Where  date (date) between    date('now', '-1 days' ) and  date('now')  group by user_id order by points  DESC limit 5 ")
    dayres= zip(dailynames,stuff)
    
    stuff = db.engine.execute("SELECT sum(points) points, user_id FROM  trips Where  date (date) between    date('now', '-30 days' ) and  date('now')  group by user_id order by points  DESC limit 5 ")
    for item in stuff:
		monthlynames.append(Users.query.filter_by( id = item.user_id).first().name)
    stuff = db.engine.execute("SELECT sum(points) points, user_id FROM  trips Where  date (date) between    date('now', '-30 days' ) and  date('now')  group by user_id order by points  DESC limit 5 ")
    monthres= zip(monthlynames,stuff)
    
    
    
    print weekres
     
    return render_template('scores.html', user = user, week = weekres, day = dayres,month = monthres)

@app.route('/register')
def register():
    '''if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        name = request.form['name']
        print name'''
        
    return render_template('register.html')

@app.route('/signin', methods = ['POST', 'GET'])
def signin():
    
    if request.method == 'POST':
        user = request.form['username']
        password = request.form['password']
        name = request.form['name']
        mpg = request.form['mpg']
        
        new_user = Users(user, password,name,mpg)
        db.session.add(new_user)
        db.session.commit()
        return'User added'
    else:
        return render_template('signin.html')

@app.route('/verifyuser', methods = ['POST', 'GET'])
def verifyuser():
    global user
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print username
        print password

        #registered_user = session.query(Users).filter(Users.username = username).filter(Users.password = password)

        #registered_user = session.query(Users).filter_by(username = username, password = password)
        
        registered_user = Users.query.filter_by(username = username, password = password).first()
        
        if registered_user is None:
            
            return 'Invalid username or password'
          
        else:
            user = registered_user
            print 'Login successful'
            print user
            return 'Login successful'

@app.route('/profile')
def profile():
	global user

	
	weektotal = None
	monthtotal = None
	trips = Trips.query.filter_by(user_id = user.id).all()	
	#result = db.session.query(Trips).filter(datetime.now() -Trips.date < timedelta ( minutes = 1)).query(Trips.user_id, label('totalpoints', func.sum(Trips.points))).group_by(Trips.user_id).all()
	month = db.engine.execute( 'SELECT sum(points) total, user_id  FROM  trips where user_id = ' + str(user.id )+ " and  date (date) between    date('now', '-30 days' ) and  date('now')   group by user_id" )
	for item in month:
		monthtotal =  item.total
	week  = db.engine.execute( 'SELECT sum(points) total, user_id  FROM  trips where user_id = ' + str(user.id )+ " and  date (date) between    date('now', '-7 days' ) and  date('now')   group by user_id" )
	for item in week:
		weektotal =  item.total

	return render_template('profile.html', user = user, trips = trips, week = weektotal, month = monthtotal)

@app.route('/create')
def create():
    global user
    
    return render_template('create.html', user = user)
    
@app.route('/details/<id>')
def details(id = None):
	global user
	bid = Bids.query.filter_by( id = id).first()
	
	return render_template('details.html', user = user, item = bid)
	
	

@app.route('/addtrip', methods = ['POST', 'GET'])
def addtrip():
    global user
    if request.method == 'POST':
		if user == None:
			return "Please signin"
		#gather reuqest data
		miles = float(request.form['miles'])
		points = (8887/ user.mpg) * .0022 * miles
		transportation = request.form['transportation']
		if transportation == "Car":
			points = points * -1
		
		new_trip = Trips( points, datetime.now(), user)
		
		
		
		db.session.add(new_trip)
		db.session.commit()
		return "Your bid was added"



if __name__ == "__main__":
    app.run(debug=True)


from flask import Flask, request, render_template, session
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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trips.db'
db = SQLAlchemy(app, session_options = { 'expire_on_commit':False})



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
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
       
    else:
        
        user = None
    
    return render_template('home.html', user = user)
@app.route('/facts', methods = ['POST', 'GET'])
def facts():
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
    
    return render_template('facts.html', user = user)
    
@app.route('/scores')
def scores():
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
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
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
        
    return render_template('register.html',user = user)

@app.route('/signin', methods = ['POST', 'GET'])
def signin():
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
    if request.method == 'POST':
        usernam = request.form['username']
        password = request.form['password']
        name = request.form['name']
        mpg = request.form['mpg']
        confirm = request.form['conf']
        if confirm != password:
            return "Passwords Don't match"
        
        new_user = Users(username, password,name,mpg)
        db.session.add(new_user)
        db.session.commit()
        return'User added'
    else:
        return render_template('signin.html', user = user)

@app.route('/verifyuser', methods = ['POST', 'GET'])
def verifyuser():
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
   
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
            session['user'] = registered_user.id
            print 'Login successful'
            print user
            return 'Login successful'

@app.route('/profile')
def profile():
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
    print user.name
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
    print "stop 1"
    return render_template('profile.html', user = user, trips = trips, week = weektotal, month = monthtotal)

@app.route('/create')
def create():
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
    
    return render_template('create.html', user = user)
    
@app.route('/about')
def about():
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
        
        
        return render_template('about.html', user = user)
        
        

@app.route('/addtrip', methods = ['POST', 'GET'])
def addtrip():
    if 'user' in session:
        user_id = session['user']
        user = Users.query.filter_by(id = user_id).first()
    else:
        user = None
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
                return "Your trip was added! Thank you"


app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
if __name__ == "__main__":
    app.run(debug=True)


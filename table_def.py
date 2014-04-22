# table_def.py
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from datetime import datetime, timedelta

engine = create_engine('sqlite:///trips.db', echo=True)
Base = declarative_base()

class Users(Base):
	""""""
	__tablename__ = "users"
	
	id = Column(Integer, primary_key=True)
	username = Column(String)
	password = Column(String)
	name = Column(String)
	mpg = Column(Integer)
	totalpoints = Column(Integer)	
	def __init__(self, user_name, password, name, mpg, totalpoint = 0):
		""""""
		self.username = user_name
		self.password = password
		self.name = name
		self.mpg = mpg
		self.totalpoints = totalpoints
	
	
 
class Trips(Base):
	""""""
	__tablename__ = "trips"
 
	id = Column(Integer, primary_key=True)
	points  = Column(Integer)
	date = Column(DateTime)
	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship('Users', backref=backref('trips'))
 
 
	def __init__(self, points, date, user):
		""""""

		self.points = points
		self.date = date
		self.user = user
		
Base.metadata.create_all(engine)

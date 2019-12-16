
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
class User(Base):
	__tablename__ = 'user'
	id = Column(Integer, primary_key=True)
	email = Column(String(64), unique=True, nullable=False)
	read = Column(Integer)
	link = Column(Boolean)
	def __repr__(self):
		return '<User %r>' % self.email
	def __init__(self, email, read, link):
		self.email = email
		self.read = read
		self.link = link
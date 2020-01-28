from sqlalchemy import Column, Integer, String, Boolean,ForeignKey, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy_imageattach.entity import Image, image_attachment

Base = declarative_base()

class Person(Base):
	__tablename__ = 'person'
	person_id = Column(Integer, primary_key=True)
	name = Column(String)
	email = Column(String)
	phone = Column(String)
	picture = Column(String)

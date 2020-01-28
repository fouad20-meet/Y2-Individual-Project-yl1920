from model import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///people.db?check_same_thread=False')
Base.metadata.create_all(engine)
DBSession = sessionmaker(bind=engine)
session = DBSession()

def add_person(name,email,phone,picture):
	person_object = Person(
		name = name,
		email=email,
		phone=phone,
		picture=picture)
	session.add(person_object)
	session.commit()

def query_by_id(person_id):
    person = session.query(Person).filter_by(person_id=person_id).first()
    return person

def delete_by_id(person_id):
	session.query(Person).filter_by(person_id=person_id).delete()
	session.commit()

def query_all():
	people = session.query(Person).all()
	return people

def update_person(person_id,name,email,phone,picture):
	person = query_by_id(person_id)
	if name != "":
		person.name=name
	if email != "":
		person.email=email
	if phone != "":
		person.phone = phone
	if picture != None:
		person.picture = picture
	session.commit()


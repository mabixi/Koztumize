from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

DATABASE = 'postgresql+psycopg2://koztumize:koztumize@macaron/koztumize'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
db = SQLAlchemy(app)


class Koztumuser(db.Model):
    user_id = db.Column('uidNumber', db.Integer, primary_key=True)
    name = db.Column('sn', db.String)
    firstname = db.Column('givenName', db.String)
    login = db.Column('uid', db.String)
    password = db.Column('userPassword', db.String)

"""
The database is created here.

"""

from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

DATABASE = 'postgresql+psycopg2://koztumize:koztumize@macaron/koztumize'

app = Flask(__name__)  # pylint: disable=C0103
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
DB = SQLAlchemy(app)


class Koztumuser(DB.Model):
    """Create the user table for Koztumize."""
    user_id = DB.Column('uidNumber', DB.Integer, primary_key=True)
    name = DB.Column('sn', DB.String)
    firstname = DB.Column('givenName', DB.String)
    login = DB.Column('uid', DB.String)
    password = DB.Column('userPassword', DB.String)

    def __init__(self, user_id, name, firstname, login, password):
        """Constructor of Koztumuser."""
        self.user_id = user_id
        self.name = name
        self.firstname = firstname
        self.login = login
        self.password = password


class GitCommit(DB.Model):
    """Create the commit table."""
    __tablename__ = 'gitcommit'
    commit = DB.Column('hash', DB.String, primary_key=True)
    author_name = DB.Column('author_name', DB.String)
    author_email = DB.Column('author_email', DB.String)
    message = DB.Column('message', DB.String)
    date = DB.Column('date', DB.String)

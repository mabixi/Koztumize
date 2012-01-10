"""
The database is created here.

"""

import sys
from flaskext.sqlalchemy import SQLAlchemy

DATABASE = 'postgresql+psycopg2://koztumize:koztumize@macaron/koztumize'


def init(app):
    """Create the init method."""
    DB = SQLAlchemy(app)

    class GitCommit(DB.Model):
        """Create the commit table."""
        __tablename__ = 'gitcommit'
        commit = DB.Column('hash', DB.String, primary_key=True)
        author_name = DB.Column('author_name', DB.String)
        author_email = DB.Column('author_email', DB.String)
        message = DB.Column('message', DB.String)
        date = DB.Column('date', DB.DateTime)

    for name, object_ in locals().items():
        setattr(sys.modules[__name__], name, object_)

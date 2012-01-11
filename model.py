# Copyright (C) 2011 Kozea
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
The database is created here.

"""

import sys
from flaskext.sqlalchemy import SQLAlchemy  # pylint: disable=F0401

DATABASE = 'postgresql+psycopg2://koztumize:koztumize@macaron/koztumize'


def init(app):
    """Create the init method."""
    DB = SQLAlchemy(app)

    # Only declarative classes: no init, no method, used only by SQLalchemy
    # pylint: disable=W0232,R0903,W0612
    class GitCommit(DB.Model):
        """Create the commit table."""
        __tablename__ = 'gitcommit'
        commit = DB.Column('hash', DB.String, primary_key=True)
        author_name = DB.Column('author_name', DB.String)
        author_email = DB.Column('author_email', DB.String)
        message = DB.Column('message', DB.String)
        date = DB.Column('date', DB.DateTime)
    # pylint: enable=W0232,R0903,W0612

    for name, object_ in locals().items():
        setattr(sys.modules[__name__], name, object_)

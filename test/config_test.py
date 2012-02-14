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
The default config file of kuztumize.

"""


# This class is a monkey, it does not use its arguments
# pylint: disable=W0613,R0201
class FakeLDAP(object):
    """Redefine the LDAP for the test suite."""
    def search_s(self, *args, **kwargs):
        """Redefine method search for the fake LDAP."""
        return[[None, {'cn': ['test'], 'mail': ['mail']}]]

    def simple_bind_s(self, *args, **kwargs):
        """Redefine method bind for the fake LDAP."""
# pylint: enable=W0613,R0201

LDAP = FakeLDAP()
LDAP_PATH = None
DOMAIN = 'test'
MODEL = 'model'
ARCHIVE = 'archive'
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://koztumize:\
koztumize@localhost/koztumize'
GIT_REMOTE = 'git://github.com/Kozea/Koztumize.git'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

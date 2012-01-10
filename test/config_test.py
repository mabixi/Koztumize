"""
The default config file of kuztumize.

"""

import os


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
ARCHIVE = os.path.join(os.path.dirname(__file__), 'archive')
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://koztumize:\
koztumize@localhost/koztumize'
GIT_REMOTE = os.path.join('/home', 'lol', 'archive')

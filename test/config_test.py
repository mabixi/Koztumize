import os


class FakeLDAP(object):
    """Redefine the LDAP for the test suite."""
    def search_s(self, *args, **kwargs):
        """Redefine method search for the fake LDAP."""
        return[[None, {'cn': ['test'], 'mail': ['mail']}]]

    def simple_bind_s(self, *args, **kwargs):
        """Redefine method bind for the fake LDAP."""

LDAP = FakeLDAP()
LDAP_PATH = None
DOMAIN = 'test'
ARCHIVE = os.path.join(os.path.dirname(__file__), 'archive')
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://koztumize:\
koztumize@macaron/koztumize'

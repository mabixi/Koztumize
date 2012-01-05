import os

LDAP_HOST = "ldap.keleos.fr"
LDAP_PATH = "ou=People,dc=keleos,dc=fr"
DOMAIN = 'kozea'
ARCHIVE = os.path.join(os.path.expanduser('~/archive'))
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://koztumize:koztumize@macaron/koztumize'

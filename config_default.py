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

import os

LDAP_HOST = "ldap.keleos.fr"
LDAP_PATH = "ou=People,dc=keleos,dc=fr"
DOMAIN = 'kozea'
ARCHIVE = os.path.join(os.path.expanduser('~/archive'))
MODEL = os.path.join(os.path.expanduser('~/models'))
SQLALCHEMY_ECHO = True
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://koztumize:\
koztumize@macaron/koztumize'

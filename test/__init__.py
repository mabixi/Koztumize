"""
Testing suite for Koztumize.

"""

import koztumize
import os
import shutil
from brigit import Git


class FakeLDAP(object):
    """Redefine the LDAP for the test suite."""
    def search_s(self, *args, **kwargs):
        """Redefine method search for the fake LDAP."""
        return[[None, {'cn': ['test'], 'mail': ['mail']}]]

    def simple_bind_s(self, *args, **kwargs):
        """Redefine method bind for the fake LDAP."""


def setup():  # pragma: no cover
    """Set up the git repository for the all the tests"""
    koztumize.DOMAIN = 'test'
    koztumize.ARCHIVE = os.path.join(os.path.dirname(__file__), 'archive')
    koztumize.LDAP = FakeLDAP()
    domain_path = os.path.join(koztumize.ARCHIVE, koztumize.DOMAIN)
    if os.path.exists(domain_path):
        shutil.rmtree(domain_path)
    os.mkdir(domain_path)
    Git.push = lambda *args, **kwargs: None
    git = Git(domain_path)
    git.init()
    git.remote(
        'add', '-t', 'archive', 'origin',
        'git://github.com/Kozea/Koztumize.git')
    git.pull()
    git.checkout('test')

"""
Testing suite for Koztumize.

"""

import koztumize
import os
import shutil
from brigit import Git


def setup():  # pragma: no cover
    """Set up the git repository for the all the tests"""
    koztumize.DOMAIN = 'test'
    koztumize.ARCHIVE = os.path.join(os.path.dirname(__file__), 'archive')
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

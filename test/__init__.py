"""
Testing suite for Koztumize.

"""

import koztumize
import os
import shutil
from brigit import Git


def setup():  # pragma: no cover
    """Set up the git repository for the all the tests"""
    koztumize.app.config.from_pyfile('test/config_test.py')
    koztumize.db_model.init(koztumize.app)
    domain_path = os.path.join(
        koztumize.app.config['ARCHIVE'], koztumize.app.config['DOMAIN'])
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

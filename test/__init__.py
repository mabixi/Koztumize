"""
Testing suite for Koztumize.

"""

import koztumize
import os
import shutil
from brigit import Git


def setup():  # pragma: no cover
    """Set up the git repository for the all the tests"""
    koztumize.app.config.from_pyfile(
        os.environ.get('KOZTUMIZE_CONFIG', 'test/config_test.py'))
    koztumize.db_model.init(koztumize.app)
    if os.path.exists(koztumize.app.config['ARCHIVE']):
        shutil.rmtree(koztumize.app.config['ARCHIVE'])
    os.mkdir(koztumize.app.config['ARCHIVE'])
    Git.push = lambda *args, **kwargs: None
    git = Git(koztumize.app.config['ARCHIVE'])
    git.init()
    git.remote(
        'add', '-t', 'archive', 'origin', koztumize.app.config['GIT_REMOTE'])
    git.pull()
    git.checkout('test')

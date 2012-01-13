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
Testing suite for Koztumize.

"""

import koztumize
from tempfile import mkdtemp
import os
import shutil
from brigit import Git

TEMP_DIR = None


def setup():
    """Set up the git repository for the all the tests"""
    global TEMP_DIR
    TEMP_DIR = mkdtemp()
    koztumize.app.config.from_pyfile(
        os.environ.get('KOZTUMIZE_CONFIG', 'test/config_test.py'))
    koztumize.db_model.init(koztumize.app)
    Git.push = lambda *args, **kwargs: None
    for repo in ('archive', 'model'):
        koztumize.app.config[repo.upper()] = os.path.join(TEMP_DIR, repo)
        git = Git(koztumize.app.config[repo.upper()])
        git.init()
        git.remote(
            'add', '-t', repo, 'origin',
            koztumize.app.config['GIT_REMOTE'])
        git.pull()
        git.checkout(repo)


def teardown():
    """Remove the temp directory after the tests.0"""
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

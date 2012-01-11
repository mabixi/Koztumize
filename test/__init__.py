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

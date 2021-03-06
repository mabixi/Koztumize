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
Test for Koztumize (all the routes are tested)

"""

import os
from .helpers import with_client, request
from . import koztumize
from flask import url_for


@with_client
def test_index(client):
    """Test the index page."""
    response = request(client.get, '/')
    assert 'Koztumize' in response.data


@with_client
def test_edit(client):
    """Test the edit page."""
    models = {
        category: os.listdir(os.path.join(
            koztumize.app.config['MODEL'], 'test', 'model', category))
        for category in os.listdir(os.path.join(
            koztumize.app.config['MODEL'], 'test', 'model'))}
    with client.application.test_request_context():
        for category in models.keys():
            for model in models[category]:
                response = request(
                    client.get, url_for(
                        'edit', category=category, filename=model))
                assert model in response.data


@with_client
def test_model(client):
    """Test the model page."""
    models = {
        category: os.listdir(os.path.join(
            koztumize.app.config['MODEL'], 'test', 'model', category))
        for category in os.listdir(os.path.join(
            koztumize.app.config['MODEL'], 'test', 'model'))}
    with client.application.test_request_context():
        for category in models.keys():
            for model in models[category]:
                response = request(
                    client.get, url_for(
                        'model', category=category, filename=model))
                assert 'test' in response.data


@with_client
def test_generate(client):
    """Test the PDF generation."""
    data = '<html></html>'
    with client.application.test_request_context():

        response = request(
            client.post, url_for('generate'), data={'html_content': data,
                                        'filename': 'test'})
        assert response.data == 'Done'
        response = request(
            client.get, url_for('get_pdf', filename='test'),
            content_type='application/pdf')
        assert response.data[:4] == '%PDF'


@with_client
def test_archive(client):
    """Test the archive page."""
    with client.application.test_request_context():
        response = request(client.get, url_for('archive'))
        assert '<html>' in response.data


@with_client
def test_modify(client):
    """Test the modify page."""
    with client.application.test_request_context():
        response = request(client.get, url_for(
            'modify', path=os.path.join('test', 'test', 'test.html'),
        version='master'))
        assert '<head>' in response.data


@with_client
def test_reader(client):
    """Test the html reader"""
    with client.application.test_request_context():
        response = request(
            client.get, url_for(
                'reader', path=os.path.join(
                    koztumize.app.config['DOMAIN'], 'test', 'test.html')))
        assert '<head>' in response.data


@with_client
def test_save(client):
    """Test the save page."""
    data = '<html><head><meta name="model" content="test/test"></head></html>'
    request(client.post, '/save', data={
        'html_content': data, 'filename': 'test', 'category': 'test'})


@with_client
def test_history_get(client):
    """Test the history_get page."""
    with client.application.test_request_context():
        response = request(
            client.get, url_for('history_get', author="Aymeric Bois"))


@with_client
def test_archive_get(client):
    """Test the archive_get page."""
    with client.application.test_request_context():
        response = request(
        client.get, 'archive_get?search=courrier')
        assert 'courrier' in response.data


@with_client
def test_stylesheet(client):
    """Test the page which returns CSS."""
    with client.application.test_request_context():
        response = request(
        client.get, url_for('stylesheet', path='test'),
            content_type='text/css')
        assert 'CSS' in response.data


@with_client
def test_model_static(client):
    """Test the model_static page."""
    with client.application.test_request_context():
        response = request(
        client.get, url_for('model_static', path=os.path.join(
            'javascript', 'test.js')), content_type='application/x-javascript')
        assert 'function' in response.data


@with_client
def test_logout(client):
    """Test the logout."""
    with client.application.test_request_context():
        response = request(client.get, '/logout')
        assert 'Veuillez vous connecter' in response.data
        response = request(client.get, '/archive')
        assert 'archive' not in response.data


@with_client
def test_login(client):
    """Test the login."""
    with client.application.test_request_context():
        request(client.post, '/login',
                data={'login': 'test', 'passwd': ''})
        request(client.post, '/login', data={'login': 'fake', 'passwd': 'lol'})
        response = request(client.get, url_for('archive'))
        assert 'archive' in response.data

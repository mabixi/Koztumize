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
            'static', 'domain', 'test', 'model', category))
        for category in os.listdir(os.path.join(
            'static', 'domain', 'test', 'model'))}
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
            'static', 'domain', 'test', 'model', category))
        for category in os.listdir(os.path.join(
            'static', 'domain', 'test', 'model'))}
    with client.application.test_request_context():
        for category in models.keys():
            for model in models[category]:
                response = request(
                    client.get, url_for(
                        'model', category=category, filename=model))
                assert 'test.css' in response.data


@with_client
def test_generate(client):
    """Test the PDF generation."""
    data = '<html>'
    response = request(
        client.post, '/generate', content_type='application/pdf',
        data={'html_content': data, 'filename': 'test'})
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
    models = []
    with client.application.test_request_context():
        for root in os.walk('test/archive/test/test'):
            for dirs in root[2]:
                models.append(os.path.join(root[0].rsplit('/')[-1], dirs))
        for model in models:
            response = request(client.get, url_for('reader',
                                                   path=os.path.join(
                                                       koztumize.DOMAIN,
                                                       model)))
            assert '<head>' in response.data


@with_client
def test_save(client):
    """Test the save page."""
    data = '<html><head><meta name="model" content="test/test"></head></html>'
    request(client.post, '/save', data={
        'html_content': data, 'filename': 'test', 'category': 'test'})

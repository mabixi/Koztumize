"""
Test for Koztumize (all the routes are tested)

"""

import os

from .helpers import with_client, request


@with_client
def test_index(client):
    """Test the index page."""
    response = request(client.get, '/')
    assert 'Koztumize' in response.data


@with_client
def test_edit(client):
    """Test the edit page."""
    models = {
        category: os.listdir('static/domain/test/model/' + category)
        for category in os.listdir('static/domain/test/model')}
    for category in models.keys():
        for model in models[category]:
            response = request(client.get,
                               os.path.join('edit', category, model))
            assert model in response.data


@with_client
def test_model(client):
    """Test the model page."""
    models = {
        category: os.listdir('static/domain/test/model/' + category)
        for category in os.listdir('static/domain/test/model')}
    for category in models.keys():
        for model in models[category]:
            response = request(client.get, os.path.join(
               'model', category,  model[:-4]))
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
    response = request(client.get, '/archive')
    assert '<html>' in response.data


@with_client
def test_modify(client):
    """Test the modify page."""
    models = {
        category: os.listdir(os.path.expanduser('~/archive/test/') + category)
        for category in os.listdir(os.path.expanduser('~/archive/test'))}
    for category in models.keys():
        for model in models[category]:
            response = request(client.get,
                               os.path.join('modify',
                                            category, model[:-5], '0'))
            assert '<html>' in response.data


@with_client
def test_reader(client):
    """Test the html reader"""
    models = {
        category: os.listdir(os.path.expanduser('~/archive/test/') + category)
        for category in os.listdir(os.path.expanduser('~/archive/test'))}
    for category in models.keys():
        for model in models[category]:
            response = request(client.get,
                               os.path.join('file', category, model[:-5]))
    assert '<head>' in response.data


@with_client
def test_save(client):
    """Test the save page."""
    data = '<head>'
    response = request(client.post, '/save', status_code=302, data={
        'html_content': data, 'filename': 'test', 'category': 'test'})

"""
Test for Koztumize (all the routes are tested)

"""

from .helpers import with_client, request
import os


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
            response = request(client.get, '/edit/' + category + '/' + model)
            assert model in response.data


@with_client
def test_model(client):
    """Test the model page."""
    models = {
        category: os.listdir('static/domain/test/model/' + category)
        for category in os.listdir('static/domain/test/model')}
    for category in models.keys():
        for model in models[category]:
            request(client.get, '/model/' + category + '/' + model[:-4])


@with_client
def test_generate(client):
    """Test the PDF generation."""
    data = '<html>'
    response = request(
        client.post, '/generate', content_type='application/pdf',
        data={'html_content': data, 'filename': 'test'})
    assert response.data[:4] == '%PDF'

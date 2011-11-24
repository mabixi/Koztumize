from .helpers import with_client


@with_client
def test_index(client):
    """Test the index page."""
    response = client.get('/')
    assert 'Koztumize' in response.data

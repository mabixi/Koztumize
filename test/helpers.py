"""
Helpers for tests, with definition of decorator and function.

"""
from koztumize import app
from functools import wraps
from nose.tools import eq_


def with_client(function):
    """Create the test_client."""
    return wraps(function)(
        lambda *args, **kwargs: function(  # pylint: disable=W0142
            client=app.test_client(), *args, **kwargs))


def request(method, route, status_code=200, content_type='text/html',
            data=None, follow_redirects=True):
    """
    Create the test_client  and check status code and content_type.

    """
    response = method(route, data=data, follow_redirects=follow_redirects)
    eq_(response.status_code, status_code)
    assert content_type in response.content_type
    return response
 
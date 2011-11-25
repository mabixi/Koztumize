"""
Helpers for tests, with definition of decorator and function.

"""
from koztumize import app
from functools import wraps
from nose.tools import eq_


def with_client(function):
    """Create the test_client."""
    return wraps(function)(lambda: function(app.test_client()))


def request(method, route, status_code=200, content_type='text/html'):
    """
    Create the test_client  and check status code and content_type.

    """
    response = method(route)
    eq_(response.status_code, status_code)
    assert content_type in response.content_type
    return response

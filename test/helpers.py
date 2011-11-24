from koztumize import app
from functools import wraps


def with_client(function):
    return wraps(function)(lambda: function(app.test_client()))

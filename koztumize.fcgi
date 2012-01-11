#!/usr/bin/env python2

import koztumize
from flup.server.fcgi import WSGIServer

WSGIServer(koztumize.app, debug=False).run()

#!/usr/bin/env python2

import koztumize
from flup.server.fcgi import WSGIServer

koztumize.db_model.init(koztumize.app)
app.config.from_pyfile('/var/www/.koztumize.config')
WSGIServer(koztumize.app, debug=False).run()

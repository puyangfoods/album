#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from werkzeug.debug import DebuggedApplication
#from flask_debugtoolbar import DebugToolbarExtension
app = Flask(__name__)
app.config.from_object('huatuo.settings')
try:
    app.config.from_envvar('HUATUO_SETTINGS')
except RuntimeError:
    print 'No env var HUATUO_SETTINGS'
#toolbar = DebugToolbarExtension(app)

app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

import huatuo.views

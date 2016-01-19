__author__ = 'Ronald'

from views_client import *

app.register_blueprint(prefix, url_prefix='/client')
app.register_blueprint(prefix_contact, url_prefix='/contact')
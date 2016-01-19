__author__ = 'Ronald'

from views_tache import *

app.register_blueprint(prefix_projet, url_prefix='/projet')
app.register_blueprint(prefix, url_prefix='/tache')
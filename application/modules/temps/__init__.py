__author__ = 'Ronald'

from views_temps import *

app.register_blueprint(prefix_tache, url_prefix='/tache')
app.register_blueprint(prefix, url_prefix='/temps')

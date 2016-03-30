__author__ = 'Ronald'

from views_temps import *
from views_temps_breack import *

app.register_blueprint(prefix_tache, url_prefix='/tache')
app.register_blueprint(prefix_tache_breack, url_prefix='/tache')
app.register_blueprint(prefix, url_prefix='/temps')

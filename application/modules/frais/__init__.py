__author__ = 'Ronald'

from views_frais import *

app.register_blueprint(prefix, url_prefix='/parametre')
app.register_blueprint(prefix_projet, url_prefix="/projet")
app.register_blueprint(prefix_tache, url_prefix="/tache")
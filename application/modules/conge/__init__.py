__author__ = 'Ronald'


from views_conge import *

app.register_blueprint(prefix, url_prefix='/permission')
app.register_blueprint(prefix_param, url_prefix='/parametre')

"""
urls.py

URL dispatch route mappings and error handlers

"""
from flask import render_template

from application import app
from application.modules import dashboard, home, user, societe, site, departement, grade, fonction, frais, domaine, profil, \
    prestation, role, budget, charge, client, projet, tache, temps, rapport

## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route('/Unauthorized')
def server_Unauthorized():
    return render_template('401.html'), 401




"""
decorators.py

Decorators for URL handlers

"""

from functools import wraps
from flask import redirect, request, abort, url_for, flash
from flask import current_app, session
from flask.ext.login import current_user


def login_required(func):
    """Requires standard login credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated() or not session.get('user_id'):
            return redirect(url_for('home.index'))

        if current_user.is_authenticated() and not current_user.is_active():
            flash('Votre compte est desactive. Contactez votre administrateur', 'danger')
            return redirect(url_for('user.logout'))

        return func(*args, **kwargs)
    return decorated_view


def roles_required(required_roles, required_droits=None):
    """Requires App Engine admin credentials"""
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated() or not session.get('user_id'):
                flash('Connectez-vous SVP.', 'danger')
                return redirect(url_for('home.index'))

            # User must have the required roles
            if not current_user.has_roles(required_roles, required_droits):
                # Redirect to the unauthorized page
                return redirect(url_for('server_Unauthorized'))

            # Call the actual view
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


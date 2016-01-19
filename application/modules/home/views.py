__author__ = 'wilrona'

from ...modules import *
from application import google_login

cache = Cache(app)
prefix = Blueprint('home', __name__)


# @app.route('/set_session')
# def set_session():
#     session.permanent = True
#     return json.dumps({
#         'statut': True
#     })


# @app.route('/', methods=['POST', 'GET'])
# def home():
#
#     time_zones = pytz.timezone('Africa/Douala')
#     date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")
#
#     if 'user_id' in session:
#         return redirect(url_for('Dashboard'))
#
#     admin_role = RoleModel.query(
#         RoleModel.name == 'super_admin'
#     ).get()
#     exist_super_admin = 0
#     if admin_role:
#         exist_super_admin = UserRoleModel.query(
#             UserRoleModel.role_id == admin_role.key
#         ).count()
#
#     exist = False
#     if exist_super_admin >= 1:
#         exist = True
#
#     url = None
#     if request.args.get('url'):
#         url = request.args.get('url')
#
#     form = FormLogin(request.form)
#
#     if form.validate_on_submit():
#         try:
#             password = hashlib.sha224(form.password.data).hexdigest()
#         except UnicodeEncodeError:
#             flash('Username or Password is invalid', 'danger')
#             return redirect(url_for('Home'))
#
#         user_login = UserModel.query(
#             UserModel.email == form.email.data,
#             UserModel.password == password
#         ).get()
#
#         if user_login is None:
#             flash('Username or Password is invalid', 'danger')
#         else:
#             if not user_login.is_active():
#                 flash('Your account is disabled. Contact Administrator', 'danger')
#                 return redirect(url_for('Home', url=url))
#
#             agency = 0
#             if user_login.agency:
#                 agency = user_login.agency.get().key.id()
#                 if not user_login.agency.get().status:
#                     flash('Your agency is disabled. Contact Administrator', 'danger')
#                     return redirect(url_for('Home', url=url))
#
#             #implementation de l'heure local
#             time_zones = pytz.timezone('Africa/Douala')
#             date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")
#
#             session['user_id'] = user_login.key.id()
#             session['agence_id'] = agency
#             user_login.logged = True
#             user_login.date_last_logged = function.datetime_convert(date_auto_nows)
#             this_login = user_login.put()
#
#             if url:
#                 return redirect(url)
#
#             return redirect(url_for('Dashboard'))
#
#     return render_template('index/home.html', **locals())
#
#
# @app.route('/logout_user')
# def logout_user():
#     if 'user_id' in session:
#         user_id = session.get('user_id')
#         UserLogout = UserModel.get_by_id(int(user_id))
#         UserLogout.logged = False
#         change = UserLogout.put()
#         if change:
#             session.pop('user_id')
#             session.pop('agence_id')
#     return redirect(url_for('Home'))


@prefix.route('/')
def index():

    from ..role.models_role import Roles
    from ..user.models_user import UserRole

    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    admin_role = Roles.query(
        Roles.valeur == 'super_admin'
    ).get()

    exist_super_admin = 0
    exist = False
    if admin_role:
        exist_super_admin = UserRole.query(
            UserRole.role_id == admin_role.key
        ).count()

    google_url = google_login.login_url(
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
        params=dict(extra='superadmin')
    )

    if exist_super_admin >= 1:
        exist = True
        google_url = google_login.login_url(
            scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
            params=dict(extra='utilisateur')
        )

    # google_url = google_login.login_url(
    #     approval_prompt='force',
    #     scopes=['https://www.googleapis.com/auth/drive'],
    #     access_type='offline'
    # )

    return render_template('user/login.html', **locals())

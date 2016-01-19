__author__ = 'Ronald'

from ...modules import *
from models_grade import Grade
from forms_grade import FormGrade

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('grade', __name__)


@prefix.route('/grade')
@login_required
@roles_required([('super_admin', 'grade')])
def index():
    menu = 'societe'
    submenu = 'entreprise'
    context = 'grade'
    title_page = 'Parametre - Grades'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Grade.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='grades')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('grade/index.html', **locals())


@prefix.route('/grade/edit',  methods=['GET', 'POST'])
@prefix.route('/grade/edit/<int:grade_id>',  methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'grade')], ['edit'])
def edit(grade_id=None):

    if grade_id:
        grades = Grade.get_by_id(grade_id)
        form = FormGrade(obj=grades)
    else:
        grades = Grade()
        form = FormGrade()

    success = False
    if form.validate_on_submit():

        grades.libelle = form.libelle.data
        grades.put()

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('grade/edit.html', **locals())


@prefix.route('/grade/delete/<int:grade_id>')
@login_required
@roles_required([('super_admin', 'grade')], ['delete'])
def delete(grade_id):
    grades = Grade.get_by_id(grade_id)
    if not grades.count_user():
        grades.key.delete()
        flash('Suppression reussie', 'success')
    else:
        flash('Impossible de supprimer', 'danger')
    return redirect(url_for('grade.index'))
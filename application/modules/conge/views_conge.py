__author__ = 'Ronald'

from ...modules import *
from ..tache.models_tache import Prestation, Tache, ndb, Users
from ..temps.models_temps import Temps, DetailTemps
from ..temps.forms_temps import FormTemps


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('conge', __name__)


@prefix.route('/')
@login_required
def index():
    title_page = 'Conge - Absence'
    menu = 'conge'

    datas = Prestation.query(
        ndb.OR(
            Prestation.sigle == 'CONG',
            Prestation.sigle == 'ABS'
        )
    )
    return render_template('conge/index.html', **locals())


@prefix.route('/temps/absence/<int:prestation_id>')
@login_required
def temps_absence(prestation_id):

    title_page = 'Conge - Absence'
    menu = 'conge'
    context = 'absence'

    current_prestation = Prestation.get_by_id(prestation_id)
    user = Users.get_by_id(int(session.get('user_id')))


    exist_tache = Tache.query(
        Tache.prestation_id == current_prestation.key,
        Tache.user_id == user.key
    ).count()

    if not exist_tache:

        tache = Tache()
        tache.titre = 'Tache pour renseigner les '+current_prestation.libelle
        tache.user_id = user.key
        tache.prestation_id = current_prestation.key
        tache.put()

        return redirect(url_for('conge.temps_absence', prestation_id=prestation_id))
    else:

        tache = Tache.query(
            Tache.prestation_id == current_prestation.key,
            Tache.user_id == user.key
        ).get()

        day = datetime.date.today().strftime('%d/%m/%Y')
        dt = datetime.datetime.strptime(day, '%d/%m/%Y')
        start = dt - timedelta(days=dt.weekday())
        end = start + timedelta(days=6)

        temps = Temps.query(
            Temps.tache_id == tache.key,
            Temps.date_start == start,
            Temps.date_end == end
        ).get()

        search = False
        q = request.args.get('q')
        if q:
            search = True
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        datas = []
        pagination = None
        if temps:
            datas = DetailTemps.query(DetailTemps.temps_id == temps.key)
            pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=datas.count(), search=search, record_name='Feuille de temps')
            datas = datas.order(-DetailTemps.date, -DetailTemps.ordre)

            if datas.count() > 25:
                if page == 1:
                    offset = 0
                else:
                    page -= 1
                    offset = page * 25
                datas = datas.fetch(limit=25, offset=offset)

        return render_template('conge/temps_absence.html', **locals())


@prefix.route('/temps/absence/edit/<int:tache_id>', methods=['GET', 'POST'])
@prefix.route('/temps/absence/edit/<int:tache_id>/<int:detail_fdt_id>', methods=['GET', 'POST'])
@login_required
def temps_absence_edit(tache_id, detail_fdt_id=None):

    tache = Tache.get_by_id(tache_id)
    context = 'absence'

    if detail_fdt_id:
        detail_fdt = DetailTemps.get_by_id(detail_fdt_id)
        form = FormTemps(obj=detail_fdt)
    else:
        detail_fdt = DetailTemps()
        form = FormTemps()

    form.jour.data = 0

    success = False
    if form.validate_on_submit():

        day = datetime.date.today().strftime('%d/%m/%Y')
        dt = datetime.datetime.strptime(day, '%d/%m/%Y')
        start = dt - timedelta(days=dt.weekday())
        end = start + timedelta(days=6)


        temps = Temps.query(
            Temps.tache_id == tache.key,
            Temps.date_start == start,
            Temps.date_end == end
        ).get()

        detail_fdt.date = function.date_convert(form.date.data)
        detail_fdt.description = form.description.data
        detail_fdt.heure = function.time_convert(form.heure.data)

        time = str(form.heure.data)
        time = time.split(':')

        conversion = 0.0

        if int(time[0]) > 0:
            conversion += float(time[0])

        if int(time[1]) > 0:
            min = float(time[1])/60
            conversion += min

        detail_fdt.conversion = conversion

        if temps:
            detail_fdt.temps_id = temps.key
        else:
            temps = Temps()
            temps.user_id = tache.user_id
            temps.date_start = function.date_convert(start)
            temps.date_end = function.date_convert(end)
            temps.tache_id = tache.key
            time = temps.put()
            detail_fdt.temps_id = time

        if not detail_fdt_id:
            ordre = 1
            exist_temps = DetailTemps.query(
                DetailTemps.temps_id == detail_fdt.temps_id
            ).count()

            if exist_temps:
                ordre += exist_temps

            detail_fdt.ordre = ordre

        detail_fdt.put()

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('temps/temps_tache_edit.html', **locals())


@prefix.route('/temps/conge/<int:prestation_id>')
@login_required
def temps_conge(prestation_id):

    title_page = 'Conge - Absence'
    menu = 'conge'
    context = 'conge'

    current_prestation = Prestation.get_by_id(prestation_id)
    user = Users.get_by_id(int(session.get('user_id')))


    exist_tache = Tache.query(
        Tache.prestation_id == current_prestation.key,
        Tache.user_id == user.key
    ).count()

    if not exist_tache:

        tache = Tache()
        tache.titre = 'Tache pour renseigner les '+current_prestation.libelle
        tache.user_id = user.key
        tache.prestation_id = current_prestation.key
        tache.put()

        return redirect(url_for('conge.temps_conge', prestation_id=prestation_id))

    else:

        tache = Tache.query(
            Tache.prestation_id == current_prestation.key,
            Tache.user_id == user.key
        ).get()

        time_zones = pytz.timezone('Africa/Douala')
        date_auto_nows = datetime.datetime.now(time_zones)

        start = function.get_first_day(date_auto_nows)
        end = function.get_last_day(date_auto_nows)

        temps = Temps.query(
            Temps.tache_id == tache.key,
            Temps.date_start == start,
            Temps.date_end == end
        ).get()

        search = False
        q = request.args.get('q')
        if q:
            search = True
        try:
            page = int(request.args.get('page', 1))
        except ValueError:
            page = 1

        datas = []
        pagination = None
        if temps:
            datas = DetailTemps.query(DetailTemps.temps_id == temps.key)
            pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=datas.count(), search=search, record_name='Feuille de temps')
            datas = datas.order(-DetailTemps.date, -DetailTemps.ordre)

            if datas.count() > 25:
                if page == 1:
                    offset = 0
                else:
                    page -= 1
                    offset = page * 25
                datas = datas.fetch(limit=25, offset=offset)

        return render_template('conge/temps_conge.html', **locals())


@prefix.route('/temps/conge/edit/<int:tache_id>', methods=['GET', 'POST'])
@prefix.route('/temps/conge/edit/<int:tache_id>/<int:detail_fdt_id>', methods=['GET', 'POST'])
@login_required
def temps_conge_edit(tache_id, detail_fdt_id=None):

    tache = Tache.get_by_id(tache_id)
    context = 'conge'

    if detail_fdt_id:
        detail_fdt = DetailTemps.get_by_id(detail_fdt_id)
        form = FormTemps(obj=detail_fdt)
    else:
        detail_fdt = DetailTemps()
        form = FormTemps()

    form.derob_day.data = 1
    form.derob.data = 1


    success = False
    if form.validate_on_submit():

        time_zones = pytz.timezone('Africa/Douala')
        date_auto_nows = datetime.datetime.now(time_zones)

        start = function.get_first_day(date_auto_nows)
        end = function.get_last_day(date_auto_nows)

        temps = Temps.query(
            Temps.tache_id == tache.key,
            Temps.date_start == start,
            Temps.date_end == end
        ).get()

        detail_fdt.date = function.date_convert(form.date.data)
        detail_fdt.description = form.description.data

        detail_fdt.jour = int(form.jour.data)

        jour = 8 * int(form.jour.data)

        if jour >= 10:
            heure = str(jour)+':00'
        else:
            heure = '0'+str(jour)+":00"

        time = str(heure)
        time = time.split(':')

        conversion = 0.0

        if int(time[0]) > 0:
            conversion += float(time[0])

        if int(time[1]) > 0:
            min = float(time[1])/60
            conversion += min

        detail_fdt.conversion = conversion

        if temps:
            detail_fdt.temps_id = temps.key
        else:
            temps = Temps()
            temps.user_id = tache.user_id
            temps.date_start = function.date_convert(start)
            temps.date_end = function.date_convert(end)
            temps.tache_id = tache.key
            time = temps.put()
            detail_fdt.temps_id = time

        if not detail_fdt_id:
            ordre = 1
            exist_temps = DetailTemps.query(
                DetailTemps.temps_id == detail_fdt.temps_id
            ).count()

            if exist_temps:
                ordre += exist_temps

            detail_fdt.ordre = ordre

        detail_fdt.put()

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('temps/temps_tache_edit.html', **locals())


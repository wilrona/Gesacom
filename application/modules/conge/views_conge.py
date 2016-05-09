__author__ = 'Ronald'

from ...modules import *
from ..tache.models_tache import Prestation, Tache, ndb, Users
from ..temps.models_temps import Temps, DetailTemps
from ..temps.forms_temps import FormTemps
from models_conge import Ferier
from forms_conge import FormFerier


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('conge', __name__)
prefix_param = Blueprint('ferier', __name__)


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
            datas = DetailTemps.query(DetailTemps.temps_id == temps.key, DetailTemps.parent == None)
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

        if detail_fdt_id:
            if detail_fdt.date != function.date_convert(form.date.data) or detail_fdt.jour != int(form.jour.data):
                delete_fdt = DetailTemps.query(
                    DetailTemps.parent == detail_fdt_id
                )
                for delete in delete_fdt:
                    delete.key.delete()

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

        parent = detail_fdt.put()
        parent = DetailTemps.get_by_id(parent.id())

        start = 0
        for day in range(0, int(form.jour.data)):
            detail_fdt = DetailTemps()
            date_1 = datetime.datetime.strptime(function.date_convert(form.date.data).strftime('%m/%d/%y'), "%m/%d/%y")
            date_2 = date_1 + timedelta(days=start)

            add = False
            if date_2.weekday() == 5:
                start += 2
                date_2 = date_1 + timedelta(days=start)
                add = True

            detail_fdt.date = date_2
            detail_fdt.conversion = 8.0
            detail_fdt.temps_id = parent.temps_id
            detail_fdt.parent = int(parent.key.id())
            detail_fdt.put()

            start += 1

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('temps/temps_tache_edit.html', **locals())


@prefix_param.route('/ferier')
@login_required
def jour_ferier():

    title_page = 'Parametre - Jour Ferier'
    menu = 'societe'
    submenu = 'ferier'

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones)

    year = date_auto_nows.year

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Ferier.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Ferier')
    datas = datas.order(-Ferier.date)
    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('conge/jour_ferier.html', **locals())


@prefix_param.route('/ferier/edit', methods=['GET', 'POST'])
@prefix_param.route('/ferier/edit/<int:ferier_id>', methods=['GET', 'POST'])
@login_required
def jour_ferier_edit(ferier_id=None):

    if ferier_id:
        feriers = Ferier.get_by_id(ferier_id)
        form = FormFerier(obj=feriers)
    else:
        feriers = Ferier()
        form = FormFerier()

    success = False
    if form.validate_on_submit():

        feriers.date = function.date_convert(form.date.data)
        feriers.description = form.description.data

        feriers.put()

        update = False
        if not ferier_id:
            time_zones = pytz.timezone('Africa/Douala')
            date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

            if function.date_convert(form.date.data) <= function.date_convert(date_auto_nows):
                update = True

        flash('Enregistement effectue avec succes', 'success')
        success = True

    return render_template('conge/jour_ferier_edit.html', **locals())


@prefix_param.route('/ferier/delete/<int:ferier_id>')
@login_required
def jour_ferier_delete(ferier_id):

    if request.args.get('confirmation'):
        return render_template('conge/jour_ferier_confirnation.html', **locals())

    ferier = Ferier.get_by_id(ferier_id)
    prest_ferier = Prestation.query(Prestation.sigle == 'FER').get()

    # Ensemble des utilisateurs
    all_user = Users.query(Users.email != 'admin@accentcom-cm.com')

    day = function.date_convert(ferier.date).strftime('%d/%m/%Y')
    dt = datetime.datetime.strptime(day, '%d/%m/%Y')
    start = dt - timedelta(days=dt.weekday())
    end = start + timedelta(days=6)


    for user in all_user:

        tache_ferier = Tache.query(
            Tache.prestation_id == prest_ferier.key,
            Tache.user_id == user.key
        ).get()

        if tache_ferier:

            the_temps_ferier = Temps.query(
                Temps.tache_id == tache_ferier.key,
                Temps.date_start == start,
                Temps.date_end == end
            ).get()

            if the_temps_ferier:

                all_detailTemps = DetailTemps.query(
                    DetailTemps.temps_id == the_temps_ferier.key,
                    DetailTemps.date == function.date_convert(ferier.date)
                )

                for detailTemps in all_detailTemps:
                    detailTemps.key.delete()

                details = DetailTemps.query(
                    DetailTemps.temps_id == the_temps_ferier.key
                ).count()

                if details:
                    the_temps_ferier.key.delete()

    ferier.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('ferier.jour_ferier'))


@prefix_param.route('/ferier/tache/refresh')
def jour_ferier_tache():

    # Ensemble des utilisateurs
    all_user = Users.query(Users.email != 'admin@accentcom-cm.com')
    prest_ferier = Prestation.query(Prestation.sigle == 'FER').get()

    for user in all_user:

        exist_tache = Tache.query(
            Tache.prestation_id == prest_ferier.key,
            Tache.user_id == user.key
        ).count()

        if not exist_tache:
            tache_conge = Tache()
            tache_conge.titre = 'Tache pour suivre les jours feriers'
            tache_conge.prestation_id = prest_ferier.key
            tache_conge.user_id = user.key
            tache_conge = tache_conge.put()

    time_zones = pytz.timezone('Africa/Douala')
    date_auto_nows = datetime.datetime.now(time_zones).strftime("%Y-%m-%d %H:%M:%S")

    all_jour_ferier = Ferier.query(
        Ferier.date <= function.date_convert(date_auto_nows),
        Ferier.apply == False
    )

    for ferier in all_jour_ferier:

        day = ferier.date.strftime('%d/%m/%Y')
        dt = datetime.datetime.strptime(day, '%d/%m/%Y')

        if dt.weekday() < 5:

            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)

            for user in all_user:

                tache = Tache.query(
                    Tache.prestation_id == prest_ferier.key,
                    Tache.user_id == user.key
                ).get()

                temps = Temps.query(
                    Temps.tache_id == tache.key,
                    Temps.date_start == start,
                    Temps.date_end == end
                ).get()

                detail_fdt = DetailTemps()
                detail_fdt.date = function.date_convert(ferier.date)
                detail_fdt.description = ferier.description
                detail_fdt.heure = function.time_convert('08:00')

                time = '08:00'
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


                ordre = 1
                exist_temps = DetailTemps.query(
                    DetailTemps.temps_id == detail_fdt.temps_id
                ).count()

                if exist_temps:
                    ordre += exist_temps

                detail_fdt.ordre = ordre

                detail_fdt.put()

            ferier.apply = True
            ferier.put()

    if request.args.get('return'):
        return redirect(url_for('ferier.jour_ferier'))
    else:
        return render_template('401.html')
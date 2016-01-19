__author__ = 'Ronald'

from ...modules import *
from ..temps.models_temps import Temps, Tache, DetailTemps, DetailFrais
from forms_temps import FormTemps


# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('temps', __name__)
prefix_tache = Blueprint('temps_tache', __name__)

@prefix.route('/')
@login_required
def index():
    menu = 'temps'
    submenu = ''
    context = ''
    title_page = 'Feuille de temps'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = Temps.query()
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='frais')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('temps/index.html', **locals())


@prefix.route('/temps/<int:temps_id>')
@login_required
def view(temps_id):

    temps = Temps.get_by_id(temps_id)

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    datas = DetailTemps.query(DetailTemps.temps_id == temps.key).order(-DetailTemps.date)
    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Feuille de temps')

    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            page -= 1
            offset = page * 10
        datas = datas.fetch(limit=10, offset=offset)

    return render_template('temps/edit.html', **locals())



@prefix_tache.route('/temps/<int:tache_id>')
@login_required
def index(tache_id):

    menu = 'tache'
    submenu = 'tache'
    context = 'fdt'
    title_page = 'Taches - Details - Feuille de temps'

    tache = Tache.get_by_id(tache_id)

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
        datas = DetailTemps.query(DetailTemps.temps_id == temps.key).order(-DetailTemps.date)

        pagination = Pagination(css_framework='bootstrap3', per_page=25, page=page, total=datas.count(), search=search, record_name='Feuille de temps')
        if datas.count() > 25:
            if page == 1:
                offset = 0
            else:
                page -= 1
                offset = page * 25
            datas = datas.fetch(limit=25, offset=offset)

    return render_template('temps/temps_tache.html', **locals())


@prefix_tache.route('/temps/edit/<int:tache_id>', methods=['GET', 'POST'])
@prefix_tache.route('/temps/edit/<int:tache_id>/<int:detail_fdt_id>', methods=['GET', 'POST'])
@login_required
def edit(tache_id, detail_fdt_id=None):

    tache = Tache.get_by_id(tache_id)

    if detail_fdt_id:
        detail_fdt = DetailTemps.get_by_id(detail_fdt_id)
        form = FormTemps(obj=detail_fdt)
    else:
        detail_fdt = DetailTemps()
        form = FormTemps()

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

        detail_fdt.put()

        flash('Enregistrement effectue avec succes', 'success')
        success = True

    return render_template('temps/temps_tache_edit.html', **locals())


@prefix_tache.route('/temps/delete/<int:detail_fdt_id>')
@login_required
def delete(detail_fdt_id):

    # information du details de la FDT
    details_temps = DetailTemps.get_by_id(detail_fdt_id)

    # Recuperation des details taches correspondant a la meme FDT de la tache a supprimer
    temps_details_count = DetailTemps.query(
        DetailTemps.temps_id == details_temps.temps_id
    )

    # Recuperation des detaisl frais correspondant a la meme FDT de la tache a supprimer
    frais_temps_count = DetailFrais.query(
        DetailFrais.temps_id == details_temps.temps_id
    )

    # id de la feuille de temps de la semaine
    temps_id = details_temps.temps_id.get().key.id()

    # id de la tache de la semaine
    tache_id = Temps.get_by_id(temps_id)
    tache_id = tache_id.tache_id.get().key.id()

    # if il n'existe plus de details temps correspondant a la FDT de la semaine, on le supprime.
    if not temps_details_count.count() and not frais_temps_count.count():
        temps = Temps.get_by_id(temps_id)
        temps.key.delete()

    details_temps.key.delete()
    flash('Suppression reussie', 'success')
    return redirect(url_for('temps_tache.index', tache_id=tache_id))



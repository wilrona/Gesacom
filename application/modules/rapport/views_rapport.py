__author__ = 'Ronald'

from ...modules import *
from ..temps.models_temps import DetailTemps, Users
from ..tache.models_tache import Tache
from ..budget.models_budget import Budget, BudgetPrestation, Prestation, Client

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('stat', __name__)


@prefix.route('/')
@login_required
@roles_required([('super_admin', 'stat')])
def index():
    menu = 'stat'
    submenu = ''
    context = 'list'
    title_page = 'Statistique et rapport'

    # Algorithme pour les dates qui se trouvent dans les details pour les filtres
    # for bud in temps_year:
    #     year = {}
    #     year['date'] = bud.date.year
    #     years.append(year)
    #
    # list_year = []
    # for key, group in groupby(years, lambda item: item["date"]):
    #     if key != now_year:
    #         if key not in list_year:
    #             list_year.append(key)
    #
    # for i in range(now_year, now_year+2):
    #     if i not in list_year:
    #         list_year.append(i)

    return render_template('rapport/index.html', **locals())


@prefix.route('/collaborateur')
@login_required
@roles_required([('super_admin', 'stat')])
def collaborateur():
    menu = 'stat'
    submenu = 'collaborateur'
    title_page = 'Remplissage des feuilles du temps par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    current_day = datetime.datetime.now(time_zones)

    temps_year = DetailTemps.query()

    analyse = []
    for detail in temps_year:
        if detail.date.month == current_month:
            if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'CONG':
                if detail.parent:
                    infos = {}
                    infos['user'] = detail.temps_id.get().user_id
                    infos['user_infos'] = 1
                    infos['tache'] = detail.temps_id.get().tache_id.get().key.id()
                    infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
                    if detail.temps_id.get().tache_id.get().facturable:
                        infos['facturable'] = 1
                    else:
                        infos['facturable'] = 0

                    infos['time'] = round(detail.conversion, 1)
                    analyse.append(infos)
            else:
                infos = {}
                infos['user'] = detail.temps_id.get().user_id
                infos['user_infos'] = 1
                infos['tache'] = detail.temps_id.get().tache_id.get().key.id()
                infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
                if detail.temps_id.get().tache_id.get().facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0

                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)


    grouper = itemgetter("user", "user_infos")

    # REGROUPEMENT DES MONTANTS PAR DESTINATION
    analyses = []

    total_abs = 0
    total_cong = 0
    total_fer = 0

    total_dev = 0
    total_adm = 0
    total_form = 0
    total_prod_fact = 0
    total_prod_nfact = 0
    total = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))
        temp_dict['dev_time'] = 0
        temp_dict['form_time'] = 0
        temp_dict['prod_time_fact'] = 0
        temp_dict['prod_time_nfact'] = 0
        temp_dict['adm_time'] = 0

        temp_dict['abs_time'] = 0
        temp_dict['cong_time'] = 0
        temp_dict['fer_time'] = 0

        temp_dict['total'] = 0

        abs_tot = 0
        cong_tot = 0
        fer_tot = 0

        dev_tot = 0
        adm_tot = 0
        prod_tot_fact = 0
        prod_tot_nfact = 0
        form_tot = 0
        for item in grp:
            if item['prestation'] == 'DEV':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']

            if item['prestation'] == 'FOR':
                temp_dict['form_time'] += item['time']
                form_tot += item['time']

            if item['prestation'] == 'ADM':
                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']

            if item['prestation'] == 'ABS':
                temp_dict['abs_time'] += item['time']
                abs_tot += item['time']

            if item['prestation'] == 'CONG':
                temp_dict['cong_time'] += item['time']
                cong_tot += item['time']

            if item['prestation'] == 'FER':
                temp_dict['fer_time'] += item['time']
                fer_tot += item['time']

            if item['prestation'] == 'PRO' and item['facturable']:
                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']

            if item['prestation'] == 'PRO' and not item['facturable']:
                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']


        temp_dict['total'] = temp_dict['prod_time_nfact']
        temp_dict['total'] += temp_dict['prod_time_fact']
        temp_dict['total'] += temp_dict['dev_time']
        temp_dict['total'] += temp_dict['adm_time']
        temp_dict['total'] += temp_dict['form_time']

        temp_dict['total'] += temp_dict['abs_time']
        temp_dict['total'] += temp_dict['cong_time']
        temp_dict['total'] += temp_dict['fer_time']

        total_dev += dev_tot
        total_adm += adm_tot
        total_prod_fact += prod_tot_fact
        total_prod_nfact += prod_tot_nfact
        total_form += form_tot

        total_abs += abs_tot
        total_cong += cong_tot
        total_fer += fer_tot

        total += temp_dict['total']

        analyses.append(temp_dict)

    return render_template('rapport/collaborateur.html', **locals())


@prefix.route('/collaborateur/refresh', methods=['GET','POST'])
def collaborateur_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))

    printer = request.args.get('print')
    title_page = 'Remplissage des feuilles du temps par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    current_day = datetime.datetime.now(time_zones)

    temps_year = DetailTemps.query(
        DetailTemps.date >= date_start,
        DetailTemps.date <= date_end
    )

    analyse = []
    for detail in temps_year:

        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'CONG':
            if detail.parent:
                infos = {}
                infos['user'] = detail.temps_id.get().user_id
                infos['user_infos'] = 1
                infos['tache'] = detail.temps_id.get().tache_id.get().key.id()
                infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
                if detail.temps_id.get().tache_id.get().facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0

                infos['time'] = round(detail.conversion, 1)
                analyse.append(infos)
        else:
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            infos['tache'] = detail.temps_id.get().tache_id.get().key.id()
            infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
            if detail.temps_id.get().tache_id.get().facturable:
                infos['facturable'] = 1
            else:
                infos['facturable'] = 0

            infos['time'] = round(detail.conversion, 1)
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    # REGROUPEMENT DES MONTANTS PAR DESTINATION
    analyses = []

    total_abs = 0
    total_cong = 0
    total_fer = 0

    total_dev = 0
    total_adm = 0
    total_form = 0
    total_prod_fact = 0
    total_prod_nfact = 0
    total = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))
        temp_dict['dev_time'] = 0
        temp_dict['form_time'] = 0
        temp_dict['prod_time_fact'] = 0
        temp_dict['prod_time_nfact'] = 0
        temp_dict['adm_time'] = 0

        temp_dict['abs_time'] = 0
        temp_dict['cong_time'] = 0
        temp_dict['fer_time'] = 0

        temp_dict['total'] = 0

        abs_tot = 0
        cong_tot = 0
        fer_tot = 0

        dev_tot = 0
        adm_tot = 0
        prod_tot_fact = 0
        prod_tot_nfact = 0
        form_tot = 0
        for item in grp:
            if item['prestation'] == 'DEV':
                temp_dict['dev_time'] += item['time']
                dev_tot += item['time']

            if item['prestation'] == 'FOR':
                temp_dict['form_time'] += item['time']
                form_tot += item['time']

            if item['prestation'] == 'ADM':
                temp_dict['adm_time'] += item['time']
                adm_tot += item['time']

            if item['prestation'] == 'ABS':
                temp_dict['abs_time'] += item['time']
                abs_tot += item['time']

            if item['prestation'] == 'CONG':
                temp_dict['cong_time'] += item['time']
                cong_tot += item['time']

            if item['prestation'] == 'FER':
                temp_dict['fer_time'] += item['time']
                fer_tot += item['time']

            if item['prestation'] == 'PRO' and item['facturable']:
                temp_dict['prod_time_fact'] += item['time']
                prod_tot_fact += item['time']

            if item['prestation'] == 'PRO' and not item['facturable']:
                temp_dict['prod_time_nfact'] += item['time']
                prod_tot_nfact += item['time']


        temp_dict['total'] = temp_dict['prod_time_nfact']
        temp_dict['total'] += temp_dict['prod_time_fact']
        temp_dict['total'] += temp_dict['dev_time']
        temp_dict['total'] += temp_dict['adm_time']
        temp_dict['total'] += temp_dict['form_time']

        temp_dict['total'] += temp_dict['abs_time']
        temp_dict['total'] += temp_dict['cong_time']
        temp_dict['total'] += temp_dict['fer_time']

        total_dev += dev_tot
        total_adm += adm_tot
        total_prod_fact += prod_tot_fact
        total_prod_nfact += prod_tot_nfact
        total_form += form_tot

        total_abs += abs_tot
        total_cong += cong_tot
        total_fer += fer_tot

        total += temp_dict['total']

        analyses.append(temp_dict)

    return render_template('rapport/collaborateur_refresh.html', **locals())


@prefix.route('/collaborateur/export/exel')
def collaborateur_export_excel():

    workbook = Workbook()
    sheet = workbook.add_sheet("Hello World")
    sheet.write(0, 0, 'Hello world!')
    out = StringIO()
    workbook.save('example.xls')

    response = make_response(out.getvalue())
    response.headers["Content-Type"] = "application/vnd.ms-excel"

    return response




@prefix.route('/taux-chargeabilite-heure-production')
@login_required
@roles_required([('super_admin', 'stat')])
def taux_HProd():
    menu = 'stat'
    submenu = 'taux_HProd'
    title_page = 'Taux du chargeabilite des heures du production'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    #Traitement du formulaire d'affichage du la liste des annees
    temps_year = DetailTemps.query(
        DetailTemps.date >= datetime.date(now_year, 1, 1)
    )

    analyse = []
    for detail in temps_year:
        if detail.date.month <= current_month:
            if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'PRO':
                infos = {}
                infos['user'] = detail.temps_id.get().user_id
                infos['user_infos'] = 1
                if detail.temps_id.get().tache_id.get().facturable:
                    infos['facturable'] = 1
                else:
                    infos['facturable'] = 0
                infos['time'] = round(detail.conversion, 1)
                infos['end'] = detail.temps_id.get().tache_id.get().end
                analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_bud = 0
    total_HP_charge = 0
    total_HP_fact = 0
    total_pourc_c = 0
    total__budget = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        if budget:

            prest_prod = Prestation.query(
                Prestation.sigle == 'PRO'
            ).get()

            budget_prod = BudgetPrestation.query(
                BudgetPrestation.budget_id == budget.key,
                BudgetPrestation.prestation_id == prest_prod.key
            ).get()

            temp_dict['budget'] = budget_prod.heure
            temp_dict['HProd_Charg'] = 0.0
            temp_dict['HProd_Fact'] = 0.0

            HProd_Charg = 0.0
            HProd_Fact = 0.0

            for item in grp:
                temp_dict['HProd_Charg'] += item['time']
                HProd_Charg += item['time']
                if item['facturable'] and item['end']:
                    temp_dict['HProd_Fact'] += item['time']
                    HProd_Fact += item['time']

            temp_dict['Pourc_Charg'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['HProd_Charg'], 1)
            temp_dict['Pourc_Bubget'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['budget'], 1)
            temp_dict['ecart'] = round((temp_dict['Pourc_Charg'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HP_charge += round(HProd_Charg, 1)
            total_HP_fact += round(HProd_Fact, 1)
            total_pourc_c += temp_dict['Pourc_Charg']
            total__budget += temp_dict['Pourc_Bubget']

            analyses.append(temp_dict)

    return render_template('rapport/taux_heure_production.html', **locals())


@prefix.route('/taux-chargeabilite-heure-production/refresh', methods=['GET','POST'])
def taux_HProd_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Taux du chargeabilite des heures du production'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year

    temps_year = DetailTemps.query(
        DetailTemps.date >= date_start,
        DetailTemps.date <= date_end
    )

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'PRO':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            if detail.temps_id.get().tache_id.get().facturable:
                infos['facturable'] = 1
            else:
                infos['facturable'] = 0
            infos['time'] = round(detail.conversion, 1)
            infos['end'] = detail.temps_id.get().tache_id.get().end
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_bud = 0
    total_HP_charge = 0
    total_HP_fact = 0
    total_pourc_c = 0
    total__budget = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        if budget:

            prest_prod = Prestation.query(
                Prestation.sigle == 'PRO'
            ).get()

            budget_prod = BudgetPrestation.query(
                BudgetPrestation.budget_id == budget.key,
                BudgetPrestation.prestation_id == prest_prod.key
            ).get()

            temp_dict['budget'] = budget_prod.heure
            temp_dict['HProd_Charg'] = 0.0
            temp_dict['HProd_Fact'] = 0.0

            HProd_Charg = 0.0
            HProd_Fact = 0.0

            for item in grp:
                temp_dict['HProd_Charg'] += item['time']
                HProd_Charg += item['time']
                if item['facturable'] and item['end']:
                    temp_dict['HProd_Fact'] += item['time']
                    HProd_Fact += item['time']

            temp_dict['Pourc_Charg'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['HProd_Charg'], 1)
            temp_dict['Pourc_Bubget'] = round((temp_dict['HProd_Fact'] * 100) / temp_dict['budget'], 1)
            temp_dict['ecart'] = round((temp_dict['Pourc_Charg'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HP_charge += round(HProd_Charg, 1)
            total_HP_fact += round(HProd_Fact, 1)
            total_pourc_c += temp_dict['Pourc_Charg']
            total__budget += temp_dict['Pourc_Bubget']

            analyses.append(temp_dict)

    return render_template('rapport/taux_heure_production_refresh.html', **locals())


@prefix.route('/taux-chargeabilite-heure-disponible')
@login_required
@roles_required([('super_admin', 'stat')])
def taux_HDispo():
    menu = 'stat'
    submenu = 'taux_HDispo'
    title_page = 'Taux du chargeabilite des heures disponibles'


    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    #Traitement du formulaire d'affichage du la liste des annees
    temps_year = DetailTemps.query(
        DetailTemps.date >= datetime.date(now_year, 1, 1)
    )

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle != 'FER':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            if detail.temps_id.get().tache_id.get().facturable:
                infos['facturable'] = 1
            else:
                infos['facturable'] = 0
            infos['time'] = round(detail.conversion, 1)
            infos['end'] = detail.temps_id.get().tache_id.get().end
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_bud = 0
    total_HDispo = 0
    total_HFact = 0
    total_pourc_c = 0
    total__budget = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        if budget:

            temp_dict['budget'] = 0.0
            if budget:
                temp_dict['budget'] = budget.heure
            temp_dict['HDispo'] = 0.0
            temp_dict['HFact'] = 0.0

            HDispo = 0.0
            HFact = 0.0

            for item in grp:
                temp_dict['HDispo'] += item['time']
                HDispo += item['time']
                if item['facturable'] and item['end']:
                    temp_dict['HFact'] += item['time']
                    HFact += item['time']

            temp_dict['Pourc_HD'] = round(((temp_dict['HFact'] * 100) / temp_dict['HDispo']), 1)
            temp_dict['Pourc_Bubget'] = round(((temp_dict['HFact'] * 100) / temp_dict['budget']), 1)
            temp_dict['ecart'] = round((temp_dict['Pourc_HD'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HDispo += round(HDispo, 1)
            total_HFact += round(HFact, 1)
            total_pourc_c += temp_dict['Pourc_HD']
            total__budget += temp_dict['Pourc_Bubget']

            analyses.append(temp_dict)

    return render_template('rapport/taux_heure_disponible.html', **locals())


@prefix.route('/taux-chargeabilite-heure-disponible/refresh', methods=['GET', 'POST'])
def taux_HDispo_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Taux du chargeabilite des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year

    temps_year = DetailTemps.query(
        DetailTemps.date >= date_start,
        DetailTemps.date <= date_end
    )

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle != 'FER':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            if detail.temps_id.get().tache_id.get().facturable:
                infos['facturable'] = 1
            else:
                infos['facturable'] = 0
            infos['time'] = round(detail.conversion, 1)
            infos['end'] = detail.temps_id.get().tache_id.get().end
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_bud = 0
    total_HDispo = 0
    total_HFact = 0
    total_pourc_c = 0
    total__budget = 0
    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        if budget:

            temp_dict['budget'] = budget.heure
            temp_dict['HDispo'] = 0
            temp_dict['HFact'] = 0

            HDispo = 0
            HFact = 0

            for item in grp:
                temp_dict['HDispo'] += item['time']
                HDispo += item['time']
                if item['facturable'] and item['end']:
                    temp_dict['HFact'] += item['time']
                    HFact += item['time']

            temp_dict['Pourc_HD'] = round(((temp_dict['HFact'] * 100) / temp_dict['HDispo']), 1)
            temp_dict['Pourc_Bubget'] = round(((temp_dict['HFact'] * 100) / temp_dict['budget']), 1)
            temp_dict['ecart'] = round((temp_dict['Pourc_HD'] - temp_dict['Pourc_Bubget']), 1)


            total_bud += temp_dict['budget']
            total_HDispo += round(HDispo, 1)
            total_HFact += round(HFact, 1)
            total_pourc_c += temp_dict['Pourc_HD']
            total__budget += temp_dict['Pourc_Bubget']

            analyses.append(temp_dict)


    return render_template('rapport/taux_heure_disponible_refresh.html', **locals())


@prefix.route('/etat-consommation-heures-disponible')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_conso():
    menu = 'stat'
    submenu = 'etat_conso'
    title_page = 'Etat du consommation des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    #Traitement du formulaire d'affichage du la liste des annees
    temps_year = DetailTemps.query(
        DetailTemps.date >= datetime.date(now_year, 1, 1)
    )

    exept_temps_year = [
        'FER',
        'ABS',
        'CONG'
    ]

    analyse = []
    for detail in temps_year:
        if detail.date.month <= current_month and detail.temps_id.get().tache_id.get().prestation_id.get().sigle not in exept_temps_year:
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
            infos['time'] = round(detail.conversion, 1)
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_budget = 0
    total_adm = 0
    total_form = 0
    total_dev = 0
    total_prod = 0

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        if budget:

            temp_dict['budget'] = budget.heure
            temp_dict['dev_time'] = 0
            temp_dict['form_time'] = 0
            temp_dict['prod_time'] = 0
            temp_dict['adm_time'] = 0

            dev_tot = 0
            adm_tot = 0
            prod_tot = 0
            form_tot = 0
            for item in grp:
                if item['prestation'] == 'DEV':
                    temp_dict['dev_time'] += item['time']
                    dev_tot += item['time']
                if item['prestation'] == 'FOR':
                    temp_dict['form_time'] += item['time']
                    form_tot += item['time']
                if item['prestation'] == 'ADM':
                    temp_dict['adm_time'] += item['time']
                    adm_tot += item['time']
                if item['prestation'] == 'PRO':
                    temp_dict['prod_time'] += item['time']
                    prod_tot += item['time']

            total_budget += temp_dict['budget']
            total_adm += adm_tot
            total_form += form_tot
            total_dev += dev_tot
            total_prod += prod_tot

            analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_disponible.html', **locals())


@prefix.route('/etat-consommation-heures-disponible/refresh', methods=['GET', 'POST'])
def etat_conso_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Etat du consommation des heures disponibles'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year

    temps_year = DetailTemps.query(
        DetailTemps.date >= date_start,
        DetailTemps.date <= date_end
    )

    exept_temps_year = [
        'FER',
        'CONG',
        'ABS'
    ]

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle not in exept_temps_year:
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
            infos['time'] = round(detail.conversion, 1)
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_budget = 0
    total_adm = 0
    total_form = 0
    total_dev = 0
    total_prod = 0

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        if budget:

            temp_dict['budget'] = budget.heure
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0

            dev_tot = 0.0
            adm_tot = 0.0
            prod_tot = 0.0
            form_tot = 0.0
            for item in grp:
                if item['prestation'] == 'DEV':
                    temp_dict['dev_time'] += item['time']
                    dev_tot += item['time']
                if item['prestation'] == 'FOR':
                    temp_dict['form_time'] += item['time']
                    form_tot += item['time']
                if item['prestation'] == 'ADM':
                    temp_dict['adm_time'] += item['time']
                    adm_tot += item['time']
                if item['prestation'] == 'PRO':
                    temp_dict['prod_time'] += item['time']
                    prod_tot += item['time']

            total_budget += temp_dict['budget']
            total_adm += adm_tot
            total_form += form_tot
            total_dev += dev_tot
            total_prod += prod_tot

            analyses.append(temp_dict)


    return render_template('rapport/etat_conso_heure_disponible_refresh.html', **locals())


@prefix.route('/etat-consommation-heure-production')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_conso_prod():
    menu = 'stat'
    submenu = 'etat_conso_prod'
    title_page = 'Solde des heures a effectuer par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    temps_year = DetailTemps.query(
            DetailTemps.date >= datetime.date(now_year, 1, 1)
        )

    exept_temps_year = [
        'FER',
        'ABS',
        'CONG'
    ]
    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle not in exept_temps_year:
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
            infos['time'] = round(detail.conversion, 1)
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_budget = 0.0
    total_budget_origine = 0.0
    total_adm = 0.0
    total_form = 0.0
    total_dev = 0.0
    total_prod = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        if budget:
            temp_dict['budget_origine'] = budget.heure
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0


            dev = 0.0
            adm = 0.0
            form = 0.0
            prod = 0.0

            for item in grp:
                if item['prestation'] == 'DEV':
                    dev += item['time']
                if item['prestation'] == 'FOR':
                    form += item['time']
                if item['prestation'] == 'ADM':
                    adm += item['time']
                if item['prestation'] == 'PRO':
                    prod += item['time']


            budget_prest = BudgetPrestation.query(
                BudgetPrestation.budget_id == budget.key
            )

            for budgets in budget_prest:
                if budgets.prestation_id.get().sigle == 'DEV':
                    temp_dict['dev_time'] = budgets.heure - dev
                    if budgets.heure - dev < 0:
                        temp_dict['dev_time'] = 0.0

                if budgets.prestation_id.get().sigle == 'FOR':
                    temp_dict['form_time'] = budgets.heure - form
                    if budgets.heure - form < 0:
                        temp_dict['form_time'] = 0.0

                if budgets.prestation_id.get().sigle == 'ADM':
                    temp_dict['adm_time'] = budgets.heure - adm
                    if budgets.heure - adm < 0:
                        temp_dict['adm_time'] = 0.0

                if budgets.prestation_id.get().sigle == 'PRO':
                    temp_dict['prod_time'] = budgets.heure - prod
                    if budgets.heure - prod < 0:
                        temp_dict['prod_time'] = 0.0


            temp_dict['budget'] = 0.0
            temp_dict['budget'] += temp_dict['dev_time']
            temp_dict['budget'] += temp_dict['form_time']
            temp_dict['budget'] += temp_dict['adm_time']
            temp_dict['budget'] += temp_dict['prod_time']

            if not temp_dict['budget']:
                temp_dict['budget'] = budget.heure

            total_budget_origine += temp_dict['budget_origine']
            total_budget += temp_dict['budget']
            total_adm += temp_dict['adm_time']
            total_form += temp_dict['form_time']
            total_dev += temp_dict['dev_time']
            total_prod += temp_dict['prod_time']

            analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_production.html', **locals())


@prefix.route('/etat-consommation-heure-production/refresh', methods=['GET', 'POST'])
def etat_conso_prod_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Solde des heures a effectuer par collaborateur'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year


    temps_year = DetailTemps.query(
        DetailTemps.date >= date_start,
        DetailTemps.date <= date_end
    )

    exept_temps_year = [
        'FER',
        'ABS',
        'CONG'
    ]

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle not in exept_temps_year:
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            infos['prestation'] = detail.temps_id.get().tache_id.get().prestation_id.get().sigle
            infos['time'] = round(detail.conversion, 1)
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_budget = 0.0
    total_budget_origine = 0.0
    total_adm = 0.0
    total_form = 0.0
    total_dev = 0.0
    total_prod = 0.0

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        if budget:

            temp_dict['budget_origine'] = budget.heure
            temp_dict['dev_time'] = 0.0
            temp_dict['form_time'] = 0.0
            temp_dict['prod_time'] = 0.0
            temp_dict['adm_time'] = 0.0

            dev = 0.0
            adm = 0.0
            form = 0.0
            prod = 0.0

            for item in grp:
                if item['prestation'] == 'DEV':
                    dev += item['time']
                if item['prestation'] == 'FOR':
                    form += item['time']
                if item['prestation'] == 'ADM':
                    adm += item['time']
                if item['prestation'] == 'PRO':
                    prod += item['time']


            budget_prest = BudgetPrestation.query(
                BudgetPrestation.budget_id == budget.key
            )

            for budgets in budget_prest:
                if budgets.prestation_id.get().sigle == 'DEV':
                    temp_dict['dev_time'] = budgets.heure - dev
                    if budgets.heure - dev < 0:
                        temp_dict['dev_time'] = 0.0

                if budgets.prestation_id.get().sigle == 'FOR':
                    temp_dict['form_time'] = budgets.heure - form
                    if budgets.heure - form < 0:
                        temp_dict['form_time'] = 0.0

                if budgets.prestation_id.get().sigle == 'ADM':
                    temp_dict['adm_time'] = budgets.heure - adm
                    if budgets.heure - adm < 0:
                        temp_dict['adm_time'] = 0.0

                if budgets.prestation_id.get().sigle == 'PRO':
                    temp_dict['prod_time'] = budgets.heure - prod
                    if budgets.heure - prod < 0:
                        temp_dict['prod_time'] = 0.0


            temp_dict['budget'] = 0.0
            temp_dict['budget'] += temp_dict['dev_time']
            temp_dict['budget'] += temp_dict['form_time']
            temp_dict['budget'] += temp_dict['adm_time']
            temp_dict['budget'] += temp_dict['prod_time']

            if not temp_dict['budget']:
                temp_dict['budget'] = budget.heure

            total_budget_origine += temp_dict['budget_origine']
            total_budget += temp_dict['budget']
            total_adm += temp_dict['adm_time']
            total_form += temp_dict['form_time']
            total_dev += temp_dict['dev_time']
            total_prod += temp_dict['prod_time']

            analyses.append(temp_dict)

    return render_template('rapport/etat_conso_heure_production_refresh.html', **locals())


@prefix.route('/heure-de-developpement-chargee')
@login_required
@roles_required([('super_admin', 'stat')])
def etat_dev_charge():
    menu = 'stat'
    submenu = 'dev_charge'
    title_page = 'Heures du developpement chargees'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    #Traitement du formulaire d'affichage du la liste des annees
    temps_year = DetailTemps.query()

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'DEV':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            if detail.temps_id.get().tache_id.get().projet_id:
                infos['ref_client'] = detail.temps_id.get().tache_id.get().projet_id.get().client_id.get().ref
                infos['client'] = detail.temps_id.get().tache_id.get().projet_id.get().client_id.get().name
                infos['prospect'] = None
                if detail.temps_id.get().tache_id.get().projet_id.get().prospect_id:
                    infos['prospect'] = detail.temps_id.get().tache_id.get().projet_id.get().prospect_id
                infos['client_ent'] = detail.temps_id.get().tache_id.get().projet_id.get().client_id.get().myself
            else:
                client_accent = Client.query(
                    Client.myself == True
                ).get()
                infos['ref_client'] = client_accent.ref
                infos['client'] = client_accent.name
                infos['prospect'] = None
                infos['client_ent'] = client_accent.myself

            infos['user_infos'] = 1
            infos['client_infos'] = 1
            infos['time'] = round(detail.conversion, 1)
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        temp_dict['clients'] = []
        under_grouper = itemgetter("ref_client", "client", "client_infos")
        temp_dict['total'] = 0
        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["ref_client", "client", "client_infos"], key))
            temp_dict_under['time'] = 0
            for item in grp:
                temp_dict_under['time'] += item['time']
                temp_dict_under['prospect'] = None
                if item['client_ent']:
                    if item['prospect']:
                        temp_dict_under['prospect'] = item['prospect']
            temp_dict['clients'].append(temp_dict_under)
            temp_dict['total'] += temp_dict_under['time']
        analyses.append(temp_dict)

    return render_template('rapport/heure-de-developpement-chargee.html', **locals())


@prefix.route('/heure-de-developpement-chargee/refresh', methods=['GET', 'POST'])
def etat_dev_charge_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Heures du developpement chargees'

    #Traitement du formulaire d'affichage du la liste des annees
    temps_year = DetailTemps.query(
        DetailTemps.date >= date_start,
        DetailTemps.date <= date_end
    )

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'DEV':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            if detail.temps_id.get().tache_id.get().projet_id:
                infos['ref_client'] = detail.temps_id.get().tache_id.get().projet_id.get().client_id.get().ref
                infos['client'] = detail.temps_id.get().tache_id.get().projet_id.get().client_id.get().name
                infos['prospect'] = None
                if detail.temps_id.get().tache_id.get().projet_id.get().prospect_id:
                    infos['prospect'] = detail.temps_id.get().tache_id.get().projet_id.get().prospect_id
                infos['client_ent'] = detail.temps_id.get().tache_id.get().projet_id.get().client_id.get().myself
            else:
                client_accent = Client.query(
                    Client.myself == True
                ).get()
                infos['ref_client'] = client_accent.ref
                infos['client'] = client_accent.name
                infos['prospect'] = None
                infos['client_ent'] = client_accent.myself

            infos['user_infos'] = 1
            infos['client_infos'] = 1
            infos['time'] = round(detail.conversion, 1)
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        temp_dict['clients'] = []
        under_grouper = itemgetter("ref_client", "client", "client_infos")
        temp_dict['total'] = 0
        for key, grp in groupby(sorted(grp, key=under_grouper), under_grouper):
            temp_dict_under = dict(zip(["ref_client", "client", "client_infos"], key))
            temp_dict_under['time'] = 0
            for item in grp:
                temp_dict_under['time'] += item['time']
                temp_dict_under['prospect'] = None
                if item['client_ent']:
                    if item['prospect']:
                        temp_dict_under['prospect'] = item['prospect']
            temp_dict['clients'].append(temp_dict_under)
            temp_dict['total'] += temp_dict_under['time']
        analyses.append(temp_dict)

    return render_template('rapport/heure-de-developpement-chargee_refresh.html', **locals())


@prefix.route('/taux-mali-global')
@login_required
@roles_required([('super_admin', 'stat')])
def taux_mali_global():
    menu = 'stat'
    submenu = 'taux_mali'
    title_page = 'Taux du mali global'

    time_zones = pytz.timezone('Africa/Douala')
    current_month = datetime.datetime.now(time_zones).month
    now_year = datetime.datetime.now(time_zones).year
    current_day = datetime.datetime.now(time_zones)
    First_day_of_year = datetime.date(now_year, 1, 1)

    #Traitement du formulaire d'affichage du la liste des annees
    temps_year = DetailTemps.query()


    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'PRO':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            if detail.temps_id.get().tache_id.get().facturable:
                infos['facturable'] = 1
            else:
                infos['facturable'] = 0
            infos['time'] = round(detail.conversion, 1)
            infos['end'] = detail.temps_id.get().tache_id.get().end
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_bud = 0
    total_facturable = 0
    total_facturee = 0
    total_mali_tech = 0
    total_mali_com = 0
    total_global = 0

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        prest_prod = Prestation.query(
            Prestation.sigle == 'PRO'
        ).get()

        budget_prod = BudgetPrestation.query(
            BudgetPrestation.budget_id == budget.key,
            BudgetPrestation.prestation_id == prest_prod.key
        ).get()

        temp_dict['budget'] = budget_prod.heure * temp_dict['user'].get().tauxH
        temp_dict['HFacturable'] = 0
        temp_dict['HFacturee'] = 0

        HFacturable = 0
        HFacturee = 0

        for item in grp:
            if item['facturable']:
                temp_dict['HFacturable'] += item['time'] * temp_dict['user'].get().tauxH
                HFacturable += item['time'] * temp_dict['user'].get().tauxH
                if item['end']:
                    temp_dict['HFacturee'] += item['time'] * temp_dict['user'].get().tauxH
                    HFacturee += item['time'] * temp_dict['user'].get().tauxH

        temp_dict['mali_tech'] = round(1 - (temp_dict['HFacturable'] / temp_dict['budget']),1)
        temp_dict['mali_com'] = 1
        if temp_dict['HFacturee']:
            temp_dict['mali_com'] = round(1 - (temp_dict['HFacturee'] / temp_dict['HFacturable']),1)
        temp_dict['mali_global'] = round(temp_dict['mali_tech'] + temp_dict['mali_com'],1)


        total_bud += temp_dict['budget']
        total_facturable += temp_dict['HFacturable']
        total_facturee += temp_dict['HFacturee']
        total_mali_tech = round(1 - (total_facturable / total_bud), 1)
        total_mali_com = round(1 - (total_facturee / total_facturable), 1)
        total_global = round(total_mali_com + total_mali_tech, 1)

        analyses.append(temp_dict)

    return render_template('rapport/taux-mali-global.html', **locals())


@prefix.route('/taux-mali-global/refresh', methods=['GET', 'POST'])
def taux_mali_global_refresh():

    if request.method == 'POST':
        date_start = function.date_convert(request.form['date_start'])
        date_end = function.date_convert(request.form['date_end'])
    else:
        date_start = function.date_convert(request.args.get('date_start'))
        date_end = function.date_convert(request.args.get('date_end'))
    printer = request.args.get('print')
    title_page = 'Taux du mali global'

    time_zones = pytz.timezone('Africa/Douala')
    now_year = datetime.datetime.now(time_zones).year

    #Traitement du formulaire d'affichage du la liste des annees
    temps_year = DetailTemps.query(
        DetailTemps.date >= date_start,
        DetailTemps.date <= date_end
    )

    analyse = []
    for detail in temps_year:
        if detail.temps_id.get().tache_id.get().prestation_id.get().sigle == 'PRO':
            infos = {}
            infos['user'] = detail.temps_id.get().user_id
            infos['user_infos'] = 1
            if detail.temps_id.get().tache_id.get().facturable:
                infos['facturable'] = 1
            else:
                infos['facturable'] = 0
            infos['time'] = round(detail.conversion, 1)
            infos['end'] = detail.temps_id.get().tache_id.get().end
            analyse.append(infos)

    grouper = itemgetter("user", "user_infos")

    analyses = []
    total_bud = 0
    total_facturable = 0
    total_facturee = 0
    total_mali_tech = 0
    total_mali_com = 0
    total_global = 0

    for key, grp in groupby(sorted(analyse, key=grouper), grouper):
        temp_dict = dict(zip(["user", "user_infos"], key))

        budget = Budget.query(
            Budget.user_id == temp_dict['user'].get().key,
            Budget.date_start == datetime.date(now_year, 1, 1)
        ).get()

        prest_prod = Prestation.query(
            Prestation.sigle == 'PRO'
        ).get()

        budget_prod = BudgetPrestation.query(
            BudgetPrestation.budget_id == budget.key,
            BudgetPrestation.prestation_id == prest_prod.key
        ).get()

        temp_dict['budget'] = budget_prod.heure * temp_dict['user'].get().tauxH
        temp_dict['HFacturable'] = 0
        temp_dict['HFacturee'] = 0

        HFacturable = 0
        HFacturee = 0

        for item in grp:
            if item['facturable']:
                temp_dict['HFacturable'] += item['time'] * temp_dict['user'].get().tauxH
                HFacturable += item['time'] * temp_dict['user'].get().tauxH
                if item['end']:
                    temp_dict['HFacturee'] += item['time'] * temp_dict['user'].get().tauxH
                    HFacturee += item['time'] * temp_dict['user'].get().tauxH

        temp_dict['mali_tech'] = round(1 - (temp_dict['HFacturable'] / temp_dict['budget']),1)
        temp_dict['mali_com'] = 1
        if temp_dict['HFacturee']:
            temp_dict['mali_com'] = round(1 - (temp_dict['HFacturee'] / temp_dict['HFacturable']),1)
        temp_dict['mali_global'] = round(temp_dict['mali_tech'] + temp_dict['mali_com'],1)


        total_bud += temp_dict['budget']
        total_facturable += temp_dict['HFacturable']
        total_facturee += temp_dict['HFacturee']
        total_mali_tech = round(1 - (total_facturable / total_bud), 1)
        total_mali_com = round(1 - (total_facturee / total_facturable), 1)
        total_global = round(total_mali_com + total_mali_tech, 1)

        analyses.append(temp_dict)

    return render_template('rapport/taux-mali-global_refresh.html', **locals())
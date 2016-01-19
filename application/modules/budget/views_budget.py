__author__ = 'Ronald'

from ...modules import *
from models_budget import Budget, BudgetPrestation, Prestation, ChargeBudget, Charge, ClientBudget, Client
from ..user.models_user import Users
from forms_budget import FormBudget

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('budget', __name__)


@prefix.route('/budget')
@login_required
@roles_required([('super_admin', 'budget_userH')])
def index():
    menu = 'societe'
    submenu = 'budget'
    context = 'collaborateur'
    title_page = 'Parametre - Budget Collaborateur'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    #liste des budgets collaborateurs
    users = Users.query(
        Users.email != 'admin@accentcom-cm.com'
    )

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year
    # date = datetime.date(date_auto_nows, 1, 1)

    if request.args.get('year') and request.args.get('year') is not None:
        current_year = int(request.args.get('year'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    budget_year = Budget.query()
    for bud in budget_year:
        year = {}
        year['date'] = bud.date_start.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    datas = users
    if users.count() > 10:
        if page == 1:
            offset = 0
        else:
            pages = page
            pages -= 1
            offset = pages * 10
        datas = users.fetch(limit=10, offset=offset)

    # Traitement du tableau des budgets a afficher
    list_budget = []
    for user in datas:
        data = {}
        data['id'] = user.key.id()
        data['full_name'] = user.first_name+" "+user.last_name
        data['taux'] = user.tauxH

        budget = Budget.query(
            Budget.date_start == datetime.date(current_year, 1, 1),
            Budget.user_id == user.key
        ).get()

        data['disponible'] = 0
        data['budget_id'] = None

        data['budget_prestation'] = []

        if budget:
            data['disponible'] = budget.heure
            data['budget_id'] = budget.key.id()

            budget_prest = BudgetPrestation.query(
                BudgetPrestation.budget_id == budget.key
            )

            for prestation in budget_prest:
                data2 = {}
                data2['id'] = prestation.prestation_id.get().key.id()
                data2['prestation'] = prestation.prestation_id.get().libelle
                data2['sigle'] = prestation.prestation_id.get().sigle
                data2['time'] = prestation.heure

                data['budget_prestation'].append(data2)

        list_budget.append(data)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=users.count(), search=search, record_name='Budget')

    return render_template('budget/index.html', **locals())


@prefix.route('/budget/valeur')
@login_required
@roles_required([('super_admin', 'budget_userV')])
def valeur():
    menu = 'societe'
    submenu = 'budget'
    context = 'collaborateur'
    title_page = 'Parametre - Budget Collaborateur'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    #liste des budgets collaborateurs
    users = Users.query(
        Users.email != 'admin@accentcom-cm.com'
    )

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year
    # date = datetime.date(date_auto_nows, 1, 1)

    if request.args.get('year') and request.args.get('year') is not None:
        current_year = int(request.args.get('year'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    budget_year = Budget.query()
    for bud in budget_year:
        year = {}
        year['date'] = bud.date_start.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    # Traitement du tableau des budgets a afficher
    list_budget = []

    datas = users
    if users.count() > 10:
        if page == 1:
            offset = 0
        else:
            pages = page
            pages -= 1
            offset = pages * 10
        datas = users.fetch(limit=10, offset=offset)

    for user in datas:
        data = {}
        data['id'] = user.key.id()
        data['full_name'] = user.first_name+" "+user.last_name
        data['taux'] = user.tauxH

        budget = Budget.query(
            Budget.date_start == datetime.date(current_year, 1, 1),
            Budget.user_id == user.key
        ).get()

        data['heure'] = 0

        if budget:
            budget_prest = BudgetPrestation.query(
                BudgetPrestation.budget_id == budget.key
            )
            for prestation in budget_prest:
                if prestation.prestation_id.get().sigle == 'PRO':
                    data['heure'] = prestation.heure
                    break

        list_budget.append(data)

    pagination = Pagination(css_framework='bootstrap3', page=page, total=users.count(), search=search, record_name='Budget')


    return render_template('budget/valeur.html', **locals())


@prefix.route('/budget/<int:user_id>/<int:page>/<int:current_year>', methods=['GET', 'POST'])
@prefix.route('/budget/<int:user_id>/<int:page>/<int:current_year>/<int:budget_id>', methods=['GET', 'POST'])
@login_required
@roles_required([('super_admin', 'budget_userH')], ['edit'])
def edit(user_id, page, current_year, budget_id=None):

    user = Users.get_by_id(user_id)

    if budget_id:
        budget = Budget.get_by_id(budget_id)

        disponible = budget.heure

        prest1 = BudgetPrestation.query(
            BudgetPrestation.budget_id == budget.key
        )

        for pres in prest1:

            if pres.prestation_id.get().sigle == 'FOR':
                formation = pres.heure
            if pres.prestation_id.get().sigle == 'DEV':
                developpement = pres.heure
            if pres.prestation_id.get().sigle == 'ADM':
                administration = pres.heure
            if pres.prestation_id.get().sigle == 'PRO':
                production = pres.heure
    else:
        budget = Budget()

    success = False
    if request.method == 'POST':
        disponible = request.form['disponible']
        production = request.form['production']
        formation = request.form['formation']
        developpement = request.form['developpement']

        dispo = int(request.form['disponible']) - int(request.form['administration'])
        dispo -= int(request.form['production'])
        dispo -= int(request.form['formation'])
        dispo -= int(request.form['developpement'])

        error = False
        if dispo > 0:
            error = True
            message = 'La somme des heures de prestation n\'est pas egale aux heures disponibles'
        if dispo < 0:
            error = True
            message = 'La somme des heures de prestation est superieure aux heures disponibles '+str(dispo)

        if not error:
            if not budget_id:
                budget.date_start = datetime.date(current_year, 1, 1)
                budget.user_id = user.key

            budget.heure = int(request.form['disponible'])
            bud_id = budget.put()

            prest = Prestation.query(
                Prestation.sigle != None
            )

            for pres in prest:

                presti = BudgetPrestation.query(
                    BudgetPrestation.prestation_id == pres.key,
                    BudgetPrestation.budget_id == bud_id
                ).get()

                if presti:

                    if pres.sigle == 'FOR':
                        presti.heure = int(request.form['formation'])
                    if pres.sigle == 'DEV':
                        presti.heure = int(request.form['developpement'])
                    if pres.sigle == 'ADM':
                        presti.heure = int(request.form['administration'])
                    if pres.sigle == 'PRO':
                        presti.heure = int(request.form['production'])

                    presti.budget_id = bud_id
                    presti.prestation_id = pres.key
                    presti.put()

                else:

                    prestis = BudgetPrestation()

                    if pres.sigle == 'FOR':
                        prestis.heure = int(request.form['formation'])
                    if pres.sigle == 'DEV':
                        prestis.heure = int(request.form['developpement'])
                    if pres.sigle == 'ADM':
                        prestis.heure = int(request.form['administration'])
                    if pres.sigle == 'PRO':
                        prestis.heure = int(request.form['production'])

                    prestis.budget_id = bud_id
                    prestis.prestation_id = pres.key
                    prestis.put()

            flash('Enregistement effectue avec succes', 'success')
            success = True

    return render_template('budget/edit.html', **locals())


# Traitement des charges et impots
@prefix.route('/budget/charge')
@login_required
@roles_required([('super_admin', 'budget_charge')])
def charge():
    menu = 'societe'
    submenu = 'budget'
    context = 'charge'
    title_page = 'Parametre - Budget Charge/Impot'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    if request.args.get('year') is not None:
        current_year = int(request.args.get('year'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    charge_year = ChargeBudget.query()
    for bud in charge_year:
        year = {}
        year['date'] = bud.date_app.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    datas = Charge.query()

    # Traitement du tableau des charges a afficher
    list_charge = []

    data_fecth = datas
    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            pages = page
            pages -= 1
            offset = pages * 10

        data_fecth = datas.fetch(limit=10, offset=offset)

    for charge in data_fecth:
        data = {}
        data['id'] = charge.key.id()
        data['name'] = charge.libelle

        charg = ChargeBudget.query(
            ChargeBudget.date_app == datetime.date(current_year, 1, 1),
            ChargeBudget.charge_id == charge.key
        ).get()

        data['montant'] = 0

        if charg:
            data['montant'] = charg.montant

        list_charge.append(data)


    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Charges')

    return render_template('budget/charge.html', **locals())


@prefix.route('/budget/charge/edit', methods=['POST'])
@login_required
@roles_required([('super_admin', 'budget_charge')], ['edit'])
def charge_edit():

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if request.form['year']:

        if page == 1:
            offset = 0
        else:
            pages = page
            pages -= 1
            offset = pages * 10

        charges = Charge.query().fetch(limit=10, offset=offset)
        for char in charges:
            budget = ChargeBudget.query(
                ChargeBudget.charge_id == char.key,
                ChargeBudget.date_app == function.date_convert(datetime.date(int(request.form['year']), 1, 1))
            ).get()

            clef = 'name['+str(char.key.id())+']'

            if budget:
                if float(request.form[clef]) > 0:
                    budget.montant = float(request.form[clef])
                    budget.put()
                else:
                    budget.key.delete()
            else:
                budget_new = ChargeBudget()
                if float(request.form[clef]) > 0:
                    budget_new.montant = float(request.form[clef])
                else:
                    budget_new.montant = float(0)
                budget_new.date_app = function.date_convert(datetime.date(int(request.form['year']), 1, 1))
                budget_new.charge_id = char.key
                budget_new.put()

        flash('Enregistrement effectue avec succes', 'success')

    return redirect(url_for('budget.charge', page=page, year=str(request.form['year'])))

@prefix.route('/budget/client')
@login_required
@roles_required([('super_admin', 'budget_client')])
def client():
    menu = 'societe'
    submenu = 'budget'
    context = 'client'
    title_page = 'Parametre - Budget Previsionnel Client'

    search = False
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    time_zones = pytz.timezone('Africa/Douala')
    current_year = datetime.datetime.now(time_zones).year
    now_year = datetime.datetime.now(time_zones).year

    if request.args.get('year') is not None:
        current_year = int(request.args.get('year'))

    #Traitement du formulaire d'affichage de la liste des annees
    years = []
    charge_year = ClientBudget.query()
    for bud in charge_year:
        year = {}
        year['date'] = bud.date_app.year
        years.append(year)

    list_year = []
    for key, group in groupby(years, lambda item: item["date"]):
        if key != now_year:
            list_year.append(key)

    for i in range(now_year, now_year+2):
        if i not in list_year:
            list_year.append(i)

    datas = Client.query(
        Client.prospect == False
    )

    data_fecth = datas
    if datas.count() > 10:
        if page == 1:
            offset = 0
        else:
            pages = page
            pages -= 1
            offset = pages * 10
        data_fecth = datas.fetch(limit=10, offset=offset)

    # Traitement du tableau des charges a afficher
    list_charge = []
    for client in data_fecth:
        data = {}
        data['id'] = client.key.id()
        data['name'] = client.name

        charg = ClientBudget.query(
            ClientBudget.date_app == datetime.date(current_year, 1, 1),
            ClientBudget.client_id == client.key
        ).get()

        data['montant'] = 0

        if charg:
            data['montant'] = charg.montant

        list_charge.append(data)


    pagination = Pagination(css_framework='bootstrap3', page=page, total=datas.count(), search=search, record_name='Clients')

    return render_template('budget/client.html', **locals())


@prefix.route('/budget/client/edit', methods=['POST'])
@login_required
@roles_required([('super_admin', 'budget_client')], ['edit'])
def client_edit():

    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if request.form['year']:

        if page == 1:
            offset = 0
        else:
            pages = page
            pages -= 1
            offset = pages * 10

        clients = Client.query().fetch(limit=10, offset=offset)

        for client in clients:
            budget = ClientBudget.query(
                ClientBudget.client_id == client.key,
                ClientBudget.date_app == function.date_convert(datetime.date(int(request.form['year']), 1, 1))
            ).get()

            clef = 'name['+str(client.key.id())+']'

            if budget:
                if float(request.form[clef]) > 0:
                    budget.montant = float(request.form[clef])
                    budget.put()
                else:
                    budget.key.delete()
            else:
                budget_new = ClientBudget()
                if float(request.form[clef]) > 0:
                    budget_new.montant = float(request.form[clef])
                else:
                    budget_new.montant = float(0)
                budget_new.date_app = function.date_convert(datetime.date(int(request.form['year']), 1, 1))
                budget_new.client_id = client.key
                budget_new.put()

        flash('Enregistrement effectue avec succes', 'success')

    return redirect(url_for('budget.client', page=page, year=request.form['year']))



__author__ = 'Ronald'

from ...modules import *
from ..societe.models_societe import Societe

# Flask-Cache (configured to use App Engine Memcache API)
cache = Cache(app)
prefix = Blueprint('dashboard', __name__)


@prefix.route('/')
@login_required
def index():
    title_page = 'Tableau de bord'

    entreprise = Societe.query().get()
    if not entreprise:
        return redirect(url_for('societe.index'))

    return render_template('dashboard/index.html', **locals())
# controllers/forecast_controller.py

from flask import Blueprint, render_template, request
from models import forecast_utils as fu

forecast_bp = Blueprint('forecast', __name__)

@forecast_bp.route('/forecast')
def index():
    # 'kind' détermine quel jeu de données charger
    kind = request.args.get('kind', 'world') 
    # 'view' détermine si on affiche Graphe ou Tableau (par défaut Graph)
    view_type = request.args.get('view', 'graph')
    
    data = []
    title = ""
    headers = []
    plot_html = None
    
    # Cette variable permet de "tromper" le header pour allumer le bon onglet
    current_tab = 'world' 

    # --- 1. PRÉVISION MONDE (Onglet: Population Mondiale) ---
    if kind == 'world':
        current_tab = 'world' # On s'associe à l'onglet World
        data = fu.get_world_forecast()
        title = "Prévisions : Population Mondiale (30 ans)"
        headers = ["Année", "Population", "Type"]
        if view_type == 'graph':
            plot_html = fu.generate_world_forecast_plot()

    # --- 2. PRÉVISION RÉGIONS (Onglet: Population par région) ---
    elif kind == 'region':
        current_tab = 'region' # On s'associe à l'onglet Region
        data = fu.get_region_forecast()
        title = "Prévisions : Par Continents"
        headers = ["Région", "Année", "Population", "Type"]
        if view_type == 'graph':
            plot_html = fu.generate_region_forecast_plot()

    # --- 3. PRÉVISION EUROPE (Onglet: Démographie européenne) ---
    elif kind == 'europe':
        current_tab = 'europe' # On s'associe à l'onglet Europe
        data = fu.get_europe_forecast()
        title = "Prévisions : Démographie Européenne"
        headers = ["Année", "Population", "Densité (hab/km²)", "Type"]
        if view_type == 'graph':
            plot_html = fu.generate_europe_forecast_plot()

    # --- 4. PRÉVISION VITALES (Onglet: Stats Vitales) ---
    elif kind == 'vital':
        current_tab = 'vital' # On s'associe à l'onglet Vital
        data = fu.get_vital_forecast()
        title = "Prévisions : Statistiques Vitales"
        headers = ["Année", "Natalité (‰)", "Mortalité (‰)", "Type"]
        if view_type == 'graph':
            plot_html = fu.generate_vital_forecast_plot()
            
    else:
        title = "Prévision inconnue"

    # On passe 'query_type=current_tab' au template.
    # Ainsi, header.html croira qu'on est sur la page 'world', 'region', etc.
    return render_template(
        'forecast.html',
        data=data,
        title=title,
        headers=headers,
        query_type=current_tab, 
        kind=kind,
        view_type=view_type,
        plot_html=plot_html
    )
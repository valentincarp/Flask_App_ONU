from flask import Blueprint, render_template, request
from models import taux_utils as tu 

ratio_bp = Blueprint('ratio_bp', __name__)

# ATTENTION : Ne rien mettre ici qui utilise 'request' !

@ratio_bp.route('/ratio')
def show_ratio():    
    # 1. Récupération des paramètres (Année)
    # C'est seulement maintenant, quand un utilisateur visite la page, que 'request' existe
    try:
        selected_year = int(request.args.get('year', 2023))
    except ValueError:
        selected_year = 2023

    # 2. Récupération des données
    available_years = tu.get_available_years()
    data = tu.get_gender_ratio(selected_year)
    
    title = f"Répartition Hommes / Femmes en {selected_year}"
    headers = ["Pays", "Année", "Taux Hommes (%)", "Taux Femmes (%)"]
    
    # 3. Gestion du Graphe vs Tableau
    view_type = request.args.get('view', 'table')
    plot_html = None
    
    if view_type == 'graph':
        plot_html = tu.generate_gender_ratio_plot(selected_year)

    # 4. Envoi à la vue
    return render_template(
        'ratio.html',
        data=data,
        title=title,
        headers=headers,
        query_type='ratio', 
        view_type=view_type,
        plot_html=plot_html,
        selected_year=selected_year,
        available_years=available_years
    )
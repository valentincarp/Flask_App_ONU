# controllers/main_controller.py

# importer les modules nécessaires
from flask import Blueprint, render_template, request # pour gérer les routes et les requêtes
from models import data_utils as du                   # pour accéder aux fonctions de manipulation des données

# Créer un Blueprint pour regrouper les routes
# Le Blueprint 'main' gère la route principale de l'application
# Le Blueprint sera enregistré dans l'application principale dans app.py
main = Blueprint('main', __name__)

# Route principale pour afficher les données
## Il n'y a qu'une seule route qui gère toutes les vues en fonction des paramètres d'URL 'query' et 'view'
## 'query' peut être 'world', 'region', 'top10', 'europe', ou 'about'
## 'view' peut être 'table', 'graph' ou 'map' suivant le type de 'query'
## Par défaut, 'query' est 'world' et 'view' est 'table'
## Exemple d'URL : /?query=region&view=graph
## Cela affichera la population par région sous forme de graphe
## Exemple d'URL : /?query=top10&view=table
## Cela affichera le top 10 des pays les plus peuplés en 2023 sous forme d'un tableau
@main.route('/')
def index():
    # Récupérer les paramètres d'URL
    query_type = request.args.get('query', 'world') # Par défaut : population mondiale
    view_type = request.args.get('view', 'table')  # Par défaut : tableau

    # Récupérer les données selon le type de requête
    # Génération des titres et en-têtes des colonnes du tableau selon le type de requête

    # Population mondiale par année
    if query_type == 'world': 
        data = du.get_world_population_by_year()
        title = "Population mondiale par année"
        headers = ["Année", "Hommes", "Femmes", "Total"]

    # Population par région et par année
    elif query_type == 'region': 
        data = du.get_population_by_region()
        title = "Population par région et par année"
        headers = ["Région", "Année", "Population"]

    # Top 10 des pays les plus peuplés par année
    elif query_type == 'top10': 
        data = du.get_top_10_countries()
        title = "Top 10 des pays les plus peuplés par année"
        headers = ["Année", "Pays", "Sous-région", "Région", "Continent", "Population"]

    # Population européenne
    elif query_type == 'europe':
        data = du.get_europe_population_by_year()
        title = "Population des pays d'Europe par année"
        headers = ["Année", "Pays", "Population", "Densité (hab/km²)"]

    # Page "A propos"
    elif query_type == 'about':
        data = du.get_about_data()
        title = "Informations sur le projet"
        headers = []
    
    else: # Type de requête inconnu
        data = []
        title = "Aucune donnée"
        headers = []

    # Génération des représentations selon le type de requête et le type de vue (graphique, carte)
    plot_html = None

    # graphe de la population mondiale par année
    if query_type == 'world' and view_type == 'graph': 
        plot_html = du.generate_population_plot()

    # graphe de la population par région et par année
    elif query_type == 'region' and view_type == 'graph': 
        plot_html = du.generate_region_plot()

    # graphe du top 10 des pays les plus peuplés
    elif query_type == 'top10' and view_type == 'graph': 
        plot_html = du.generate_top_10_bar_plot()

    # Carte choroplèthe de la densité de population des pays européens en 2023
    elif query_type == 'europe' and view_type == 'dens_map':
        plot_html = du.generate_europe_dens_map()

    # Rendre le template avec les données, le titre, les en-têtes, le type de requête, le type de vue et le graphe (si applicable)
    return render_template(
        'index.html',
        data=data,
        title=title,
        headers=headers,
        query_type=query_type,
        view_type=view_type,
        plot_html=plot_html
    )

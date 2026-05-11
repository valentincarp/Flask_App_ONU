from flask import Blueprint, render_template, request
from models.migration_models import (
    get_migration_rate_by_year,
    get_migration_rate_filtered,
    get_available_years,
    generate_migration_pie_chart,
    get_all_countries_with_migration
)

migration = Blueprint('migration', __name__)

@migration.route('/migration')
def migration_view():
    view_type = request.args.get('view', 'table')
    
    if view_type == 'table':
        # Récupérer les paramètres de filtrage
        selected_countries = request.args.getlist('countries')  # Liste des pays
        year_start = request.args.get('year_start', '')
        year_end = request.args.get('year_end', '')
        
        # Convertir les années en int si elles existent
        year_start_int = int(year_start) if year_start else None
        year_end_int = int(year_end) if year_end else None
        
        # Appliquer les filtres
        if selected_countries or year_start_int or year_end_int:
            data = get_migration_rate_filtered(
                countries=selected_countries if selected_countries else None,
                year_start=year_start_int,
                year_end=year_end_int
            )
        else:
            # Si aucun filtre, afficher toutes les données
            data = get_migration_rate_by_year()
        
        plot_html = None
        available_years = get_available_years()
        countries = get_all_countries_with_migration()
        selected_year = None
        top_n = 10
        
    elif view_type == 'graph':
        data = []
        available_years = get_available_years()
        selected_year = int(request.args.get('year', 2023))
        top_n = int(request.args.get('top_n', 10))
        
        plot_html = generate_migration_pie_chart(year=selected_year, top_n=top_n)
        countries = []
        selected_countries = []
        year_start = ''
        year_end = ''
        
    else:
        data = []
        plot_html = None
        available_years = []
        selected_year = None
        top_n = 10
        countries = []
        selected_countries = []
        year_start = ''
        year_end = ''
    
    return render_template(
        "migration.html",
        title="Taux de migration internationale",
        query_type="migration",
        view_type=view_type,
        data=data,
        plot_html=plot_html,
        available_years=available_years,
        selected_year=selected_year,
        top_n=top_n,
        countries=countries,
        selected_countries=request.args.getlist('countries'),
        year_start=request.args.get('year_start', ''),
        year_end=request.args.get('year_end', '')
    )
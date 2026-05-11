# ratio_male_controller.py
from flask import Blueprint, render_template, request, jsonify
from models import ratio_male_utils as rmu
import pandas as pd
import plotly.graph_objects as go
import plotly

ratio_male = Blueprint('ratio_male', __name__)

@ratio_male.route('/ratio_male')
def show_ratio_male():    
    query_type = request.args.get('query', 'ratio_country')
    view_type = request.args.get('view', 'table')
    title = "Ratio hommes/femmes 1950–2023"
    
    # Pour les deux vues, on prépare les données des 3 niveaux géographiques
    countries_data = rmu.get_sex_ratio_data_country()
    regions_data = rmu.get_sex_ratio_data_region()
    subregions_data = rmu.get_sex_ratio_data_subregion()
    
    # Conversion en DataFrame
    df_countries = pd.DataFrame(countries_data)
    df_regions = pd.DataFrame(regions_data)
    df_subregions = pd.DataFrame(subregions_data)
    
    # Extraction des listes uniques
    countries = sorted(df_countries['country_name'].unique().tolist()) if not df_countries.empty else []
    regions = sorted(df_regions['country_name'].unique().tolist()) if not df_regions.empty else []
    subregions = sorted(df_subregions['country_name'].unique().tolist()) if not df_subregions.empty else []
    years = sorted(df_countries['year'].unique().tolist()) if not df_countries.empty else []
    
    return render_template(
        "ratio_male.html",
        title=title,
        countries=countries,
        regions=regions,
        subregions=subregions,
        years=years,
        view_type=view_type,
        query_type=query_type,
    )


@ratio_male.route('/api/ratio_male_table')
def get_ratio_male_table():
    """
    API pour récupérer les données du tableau en fonction des filtres
    Gère les 3 niveaux géographiques : pays, région, sous-région
    """
    # Récupération des paramètres de la requête
    geo_level = request.args.get('geo_level', 'country')
    location_name = request.args.get('location')  # Optionnel
    year = request.args.get('year', type=int)  # Optionnel
    
    # Sélection de la fonction appropriée selon le niveau géographique
    if geo_level == 'country':
        sex_ratio_data = rmu.get_sex_ratio_data_country()
    elif geo_level == 'region':
        sex_ratio_data = rmu.get_sex_ratio_data_region()
    elif geo_level == 'subregion':
        sex_ratio_data = rmu.get_sex_ratio_data_subregion()
    else:
        return jsonify({
            'success': False,
            'message': 'Niveau géographique invalide'
        })
    
    # Filtrage optionnel des données
    filtered_data = sex_ratio_data
    
    if location_name:
        filtered_data = [
            row for row in filtered_data 
            if row['country_name'] == location_name
        ]
    
    if year:
        filtered_data = [
            row for row in filtered_data 
            if row['year'] == year
        ]
    
    return jsonify({
        'success': True,
        'data': filtered_data,
        'count': len(filtered_data)
    })


@ratio_male.route('/api/ratio_male_chart')
def get_ratio_male_chart():
    """
    API pour générer le graphique Plotly en format JSON
    Gère les 3 niveaux géographiques : pays, région, sous-région
    """
    # Récupération des paramètres de la requête
    geo_level = request.args.get('geo_level', 'country')
    location_name = request.args.get('location')
    year = request.args.get('year', type=int)
    
    # Sélection de la fonction appropriée selon le niveau géographique
    if geo_level == 'country':
        sex_ratio_data = rmu.get_sex_ratio_data_country()
    elif geo_level == 'region':
        sex_ratio_data = rmu.get_sex_ratio_data_region()
    elif geo_level == 'subregion':
        sex_ratio_data = rmu.get_sex_ratio_data_subregion()
    else:
        return jsonify({
            'success': False,
            'message': 'Niveau géographique invalide'
        })
    
    # Filtrer les données pour le lieu et l'année sélectionnés
    filtered_data = [
        row for row in sex_ratio_data 
        if row['country_name'] == location_name and row['year'] == year
    ]
    
    # Si des données sont trouvées
    if filtered_data:
        data = filtered_data[0]
        
        # Calcul du pourcentage d'hommes et de femmes
        ratio = data['sex_ratio_population']
        
        # Calcul des pourcentages sur 100
        total = 100 + ratio
        percentage_men = (ratio / total) * 100
        percentage_women = (100 / total) * 100
        
        # Définir le label selon le niveau géographique
        if geo_level == 'country':
            geo_label = 'Pays'
        elif geo_level == 'region':
            geo_label = 'Région'
        else:
            geo_label = 'Sous-région'
        
        # Création du graphique donut avec Plotly
        labels = ['Hommes', 'Femmes']
        values = [percentage_men, percentage_women]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=0.4,
            marker=dict(
                colors=['#42A5F5', '#EC407A'],
                line=dict(color='#ffffff', width=2)
            ),
            textinfo='label+percent',
            textfont=dict(size=16),
            hovertemplate='<b>%{label}</b><br>%{value:.2f}%<br><extra></extra>'
        )])
        
        # Configuration du titre et de la mise en page
        fig.update_layout(
            title={
                'text': f'Répartition hommes/femmes<br>{geo_label} : {location_name} ({year})',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Arial, sans-serif'}
            },
            annotations=[{
                'text': f'Ratio: {ratio:.2f}<br>H pour 100 F',
                'x': 0.5,
                'y': 0.5,
                'font': {'size': 14},
                'showarrow': False
            }],
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5,
                font=dict(size=14)
            ),
            height=500,
            margin=dict(t=100, b=50, l=50, r=50)
        )
        
        # Convertir le graphique en JSON
        graphJSON = plotly.io.to_json(fig)
        
        return jsonify({
            'success': True,
            'graphJSON': graphJSON,
            'location': location_name,
            'year': year,
            'geo_level': geo_label,
            'percentage_men': round(percentage_men, 2),
            'percentage_women': round(percentage_women, 2),
            'ratio': round(ratio, 2)
        })
    else:
        return jsonify({
            'success': False,
            'message': f'Aucune donnée disponible pour {location_name} en {year}'
        })
# models/data_utils.py

# modules nécessaires
import config               # importer la configuration de l'application
from models.db_utils import get_db_connection # pour se connecter à la base de données
import json                 # pour manipuler les données GeoJSON
import plotly.express as px # pour la création de graphiques interactifs
import pandas as pd         # pour la manipulation et l'analyse des données 
import folium               # pour la création de cartes interactives



###################################################################
# Population mondiale par sexe et par année (item "Population mondiale")
def get_world_population_by_year():
    # Connection à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL pour obtenir la population mondiale par sexe et par année en additionnant chaque région
    query = """
        SELECT
            year,
            SUM(CASE WHEN   fp."MALE POPULATION. AS OF 1 JULY (THOUSANDS)" IS NOT NULL
                     THEN fp."MALE POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000
                     ELSE 0 END) AS male_population,
            SUM(CASE WHEN   fp."FEMALE POPULATION. AS OF 1 JULY (THOUSANDS)" IS NOT NULL
                     THEN fp."FEMALE POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000   
                     ELSE 0 END) AS female_population,
            SUM(CASE WHEN fp."MALE POPULATION. AS OF 1 JULY (THOUSANDS)" IS NOT NULL
                     THEN fp."MALE POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000
                     ELSE 0 END) +
            SUM(CASE WHEN fp."FEMALE POPULATION. AS OF 1 JULY (THOUSANDS)" IS NOT NULL
                     THEN fp."FEMALE POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000
                     ELSE 0 END) AS total_population
        FROM
            fact_population fp
        WHERE
            fp.location_code IN (SELECT location_code FROM region)
        GROUP BY
            fp.year
        ORDER BY
            fp.year;
    """

    # Exécuter la requête, récupérer et renvoyer les résultats
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Génération du graphe de la population mondiale par sexe et par année avec Plotly
# courbes empilées + population totale (H+F)
def generate_population_plot():
    # Récupérer les données
    data = get_world_population_by_year()

    # Créer un DataFrame Pandas avec les données
    df = pd.DataFrame(data, columns=["Année", "Hommes", "Femmes", "Total"])

    # Créer le graphe par sexe avec Plotly
    fig = px.area(
        df,
        x="Année",
        y=["Hommes", "Femmes"],
        title="Évolution de la population mondiale par sexe",
        labels={"value": "Population", "Année": "Année", "variable": "Sexe"},
    )

    # Ajouter la courbe de la population totale sur le graphe
    fig.add_scatter(
        x=df["Année"],
        y=df["Total"],
        mode="lines",
        name="Total (H+F)",
        line=dict(color="black", width=4),
        opacity=0.7,
    )

    # Mettre à jour la mise en page du graphe
    fig.update_layout(
        xaxis_title="Année",
        yaxis_title="Population mondiale",
        hovermode="x unified",
    )

    # Rendre le graphe en HTML
    return fig.to_html(full_html=False)

###################################################################
# Récupérer la population par région et par année (item "Population par région")
def get_population_by_region():
    # Connection à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL pour obtenir la population par région et par année
    query = """
        SELECT
            r.name AS region_name,
            fp.year,
            SUM(fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000) AS total_population
        FROM
            fact_population fp
        JOIN
            region r ON fp.location_code = r.location_code
        GROUP BY
            r.name, fp.year
        ORDER BY
            r.name, fp.year;
    """

    # Exécuter la requête, récupérer et renvoyer les résultats
    cursor.execute(query)
    # Récupérer toutes les lignes de résultats
    results = cursor.fetchall()
    # Fermer la connexion
    conn.close()
    return results

# Génération du graphe des populations par région et année avec Plotly
def generate_region_plot():
    # Récupérer les données de population par région
    data = get_population_by_region()

    # Créer un DataFrame Pandas avec les données
    df = pd.DataFrame(data, columns=["Région", "Année", "Population"])

    # Créer le graphe avec Plotly
    fig = px.line(df, x="Année", y="Population", color="Région",
                  title="Évolution de la population par région",
                  markers=True)    
    fig.update_layout(
        xaxis_title="Année",
        yaxis_title="Population",
        hovermode="x unified",
    )

    # Rendre le graphe en HTML
    return fig.to_html(full_html=False)

###################################################################
# Récupérer le top 10 des pays les plus peuplés en 2023 (item "Top 10 des pays par année")
def get_top_10_countries():
    # Connection à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL pour obtenir le top 10 des pays les plus peuplés en 2023
    query = """
        SELECT
            year,
            country_name,
            subregion_name,
            region_name,
            continent_name,
            population
        FROM (
            SELECT
                fp.year,
                c.name AS country_name,
                sr.name AS subregion_name,
                r.name AS region_name,
                ct.name AS continent_name,
                fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000 AS population,
                ROW_NUMBER() OVER (
                    PARTITION BY fp.year
                    ORDER BY fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000 DESC
                ) AS rn
            FROM fact_population fp
            JOIN country c ON fp.location_code = c.location_code
            JOIN subregion sr ON c.parent_code = sr.location_code
            JOIN region r ON sr.parent_code = r.location_code
            JOIN continent ct ON r.parent_code = ct.location_code
        )
        WHERE rn <= 10
        ORDER BY year, population DESC;
    """

    # Exécuter la requête, récupérer et renvoyer les résultats
    cursor.execute(query)
    # Récupérer toutes les lignes de résultats
    results = cursor.fetchall()
    # Fermer la connexion
    conn.close()
    return results

# Génération du graphe en barres du top 10 des pays les plus peuplés en 2023 avec Plotly
def generate_top_10_bar_plot():
    # Récupérer les données du top 10 des pays les plus peuplés en 2023
    data = get_top_10_countries()

    # Créer un DataFrame Pandas avec les données
    df = pd.DataFrame(data, columns=[ "Année", "Pays", "Sous-région", "Région", "Continent", "Population"])

    # Créer le graphe en barres avec Plotly
    fig = px.bar(
        df,
        x="Pays",
        y="Population",
        labels={"Population": "Population", "Pays": "Pays"},
        color_discrete_sequence=["#F3B94E"],
        animation_frame="Année",
        title="Top 10 des pays les plus peuplés suivant l'année",
    )
    ymax = 1.2*df["Population"].max()
    fig.update_layout(
        xaxis_title="Pays",
        yaxis_title="Population",
        xaxis={
            'categoryorder': 'total descending',
            'tickangle': 10   # noms horizontaux
        },
        yaxis=dict(range=[0, ymax]) # Axe fixe du bas à 0 et du haut au max global
    )

    # Rendre le graphe en HTML
    return fig.to_html(full_html=False)

###################################################################
# Population et densité par pays d'Europe et par année (item "Démographie européenne")
def get_europe_population_by_year():
    # Connection à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()

    # SQL pour obtenir la population des pays européens par année
    query = """
    SELECT
        fp.year,
        c.name AS country_name,
        fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000 AS population,
        fp."POPULATION DENSITY. AS OF 1 JULY (PERSONS PER SQUARE KM)" AS population_density
    FROM
        fact_population fp
    JOIN
        country c ON fp.location_code = c.location_code
    JOIN
        subregion s ON c.parent_code = s.location_code
    JOIN
        region r ON s.parent_code = r.location_code
    WHERE
        r.name = 'Europe'
    ORDER BY
        c.name, fp.year;
    """

    # Exécuter la requête, récupérer et renvoyer les résultats
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Génération de la carte de la densité de population des pays d'Europe en 2023 avec Folium
def generate_europe_dens_map():
    # Récupérer les données de population des pays d'Europe par année
    data = get_europe_population_by_year()

    # Créer un DataFrame Pandas avec les données
    df = pd.DataFrame(data, columns=["Année", "Pays", "Population", "Densité"])


    # Choisir l'année 2023
    latest_year = 2023
    df_latest = df[df["Année"] == latest_year] # Filtrer pour l'année 2023

    # on supprime les pays suivants car ils faussent la carte (densité trop élevée pour leur petite surface)
    df_latest = df_latest[df_latest["Pays"] != "Monaco"]
    df_latest = df_latest[df_latest["Pays"] != "Gibraltar"]    
    df_latest = df_latest[df_latest["Pays"] != "Holy See"]
    df_latest = df_latest[df_latest["Pays"] != "Malta"]
    df_latest = df_latest[df_latest["Pays"] != "San Marino"]
    df_latest = df_latest[df_latest["Pays"] != "Guernsey"]
    df_latest = df_latest[df_latest["Pays"] != "Jersey"]

    # Charger le GeoJSON des pays du monde entier (frontières avec une précision variable)
    geojson_url = config.GEOJSON_10M # Choix de la résolution 10M pour un bon compromis
    with open(geojson_url, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    # Liste des pays concernés (Europe)
    europe_countries = df_latest["Pays"].unique().tolist()

    # Injecter la densité dans les propriétés du GeoJSON
    dens_dict = df_latest.set_index("Pays")["Densité"].to_dict()

    # Filtrer les features du GeoJSON pour ne garder que les pays européens
    filtered_features = []
    for feature in geojson_data["features"]:
        country_name = feature["properties"].get("NAME_ENGL")
        if country_name in europe_countries:
            feature["properties"]["DENSITÉ"] = float(dens_dict[country_name])
            filtered_features.append(feature)

    geojson_data["features"] = filtered_features

    # Construire la carte
    m = folium.Map(
        location=[60, 74],
        zoom_start=3,
        width="100%",
        height="450px"
    )

    # Carte choroplèthe pour la densité 2023
    folium.Choropleth(
        geo_data=geojson_data,
        name="Densité de population",
        data=df_latest,
        columns=["Pays", "Densité"],
        key_on="feature.properties.NAME_ENGL",
        fill_color="YlGnBu",                       # Palette de couleurs, jaune à bleu
        # échelle logarithmique pour mieux visualiser les différences de densité
        bins=[0, 50, 100, 200, 400, df_latest["Densité"].max()],
        fill_opacity=0.6,
        line_opacity=0.4,
        nan_fill_color="white",
        legend_name=f"Densité de population en {latest_year} (hab/km²)",
    ).add_to(m)

    # ---Contours + Tooltip avec population---
    folium.GeoJson(
        geojson_data,                                # Données GeoJSON, filtrées pour l'Europe
        name="Limites des pays européens",           # Nom de la couche
        style_function=lambda x: {'weight': 1,       # Épaisseur des contours
                                  'color': 'black',  # Couleur des contours
                                  'fillOpacity': 0}, # Opacité de remplissage
        tooltip=folium.GeoJsonTooltip(               # Tooltip avec nom du pays et population
            fields=["NAME_ENGL", "DENSITÉ"],      # Champs à afficher dans le tooltip
            aliases=["Pays :", f"Densité en {latest_year} (hab/km²) :"], # Alias pour les champs
            localize=True, 
            labels=True
        )
    ).add_to(m) # Ajouter à la carte

    # Ajout d'un titre superposé à la carte en haut à gauche
    title_html = f'''
            <div style="position: fixed;
                        top: 10px; left: 50px; width: auto; height: auto;
                        z-index:9999;
                        font-size:16px;
                        background-color: #f8eaca77;
                        padding: 5px;
                        border-radius: 5px;
                        border: 1px solid grey;
                        box-shadow: 3px 3px 5px rgba(0,0,0,0.4);">
                Densité de population des pays d'Europe en {latest_year}
            </div>
             '''
    m.get_root().html.add_child(folium.Element(title_html))


    # Rendre la carte en HTML
    return m._repr_html_()

###################################################################
# Récupérer les informations sur le projet (item "À propos")
def get_about_data():
    # Informations sur le projet sous forme de liste de listes
    # Une liste interne par information (clé, valeur)
    about = [
        ["Projet", "Visualisation des données de population mondiale de 1950 à 2023"],
        ["Source(s) des données", "Base de données World Population Prospects 2024 de l'ONU"],
        ["Lien(s) vers les données", "<a href='https://population.un.org/wpp/downloads?folder=Standard' target='_blank'>https://population.un.org/wpp/downloads?folder=Standard</a>"],
        ["Auteur(s) du projet", "Nom(s) de l'auteur ou des auteurs"],
        ["Institution", "IUT de Créteil-Vitry, département Informatique"],
        ["Formation", "BUT Informatique - 1ère année - Semestre 1"],
        ["Année", "2025-2026"],
        ["Description", "Cette application permet de visualiser les données de population mondiale par année, par région, de consulter le top 10 des pays les plus peuplés, ou d'explorer la démographie européenne."],
        ["Fonctionnalités", "Affichage des données sous forme de tableaux, graphiques interactifs, cartes et indicateurs clés."],
        ["Technologies utilisées", "<a href='https://www.python.org/' target='_blank'>Python</a>, \
                                    <a href='https://flask.palletsprojects.com/' target='_blank'>Flask</a>, \
                                    <a href='https://www.sqlite.org/index.html' target='_blank'>SQLite</a>, \
                                    <a href='https://plotly.com/' target='_blank'>Plotly</a>, \
                                    <a href='https://pandas.pydata.org/' target='_blank'>Pandas</a>, \
                                    <a href='https://datatables.net/' target='_blank'>DataTables</a>, \
                                    <a href='https://python-visualization.github.io/folium/' target='_blank'>Folium</a>. "],
    ]

    # Renvoyer les informations
    return about

from models.db_utils import get_db_connection
import plotly.express as px
import pandas as pd

def get_migration_rate_by_year():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            fp.year,
            fp.[NET MIGRATION RATE (PER 1.000 POPULATION)] AS Taux,
            c.name
        FROM fact_population fp
        JOIN country c 
            ON fp.location_code = c.location_code
        WHERE fp.year BETWEEN 1950 AND 2023
        ORDER BY fp.year;
    """

    cursor.execute(query)
    results = cursor.fetchall()
    results_as_tuples = [tuple(row) for row in results]

    cursor.close()
    conn.close()
    
    return results_as_tuples


def get_available_years():
    """Récupère la liste des années disponibles"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT DISTINCT year FROM fact_population WHERE year BETWEEN 1950 AND 2023 ORDER BY year DESC;"
    cursor.execute(query)
    results = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    return results


def get_migration_data_for_year(year):
    """Récupère les données de migration pour une année donnée"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            c.name AS country,
            fp.[NET MIGRATION RATE (PER 1.000 POPULATION)] AS migration_rate
        FROM fact_population fp
        JOIN country c ON fp.location_code = c.location_code
        WHERE fp.year = ?
            AND fp.[NET MIGRATION RATE (PER 1.000 POPULATION)] IS NOT NULL
        ORDER BY ABS(fp.[NET MIGRATION RATE (PER 1.000 POPULATION)]) DESC;
    """

    cursor.execute(query, (year,))
    results = cursor.fetchall()
    results_as_tuples = [tuple(row) for row in results]

    cursor.close()
    conn.close()
    
    return results_as_tuples


def generate_migration_pie_chart(year=2023, top_n=10):
    """Génère un camembert des pays avec les taux de migration les plus élevés"""
    data = get_migration_data_for_year(year)
    
    if not data:
        return "<p>Aucune donnée disponible pour cette année.</p>"
    
    # Créer un DataFrame
    df = pd.DataFrame(data, columns=["Pays", "Taux de migration"])
    
    # Séparer les migrations positives et négatives
    df_positive = df[df["Taux de migration"] > 0].nlargest(top_n // 2, "Taux de migration")
    df_negative = df[df["Taux de migration"] < 0].nsmallest(top_n // 2, "Taux de migration")
    
    # Combiner les deux
    df_top = pd.concat([df_positive, df_negative])
    
    # Utiliser la valeur absolue pour le camembert
    df_top["Taux absolu"] = df_top["Taux de migration"].abs()
    
    # Créer des labels avec le signe
    df_top["Label"] = df_top.apply(
        lambda row: f"{row['Pays']} ({row['Taux de migration']:+.2f})", 
        axis=1
    )
    
    # Créer le graphique camembert
    fig = px.pie(
        df_top,
        values="Taux absolu",
        names="Label",
        title=f"Top {top_n} des pays par taux de migration en {year}<br>(valeurs absolues)",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.3
    )
    
    fig.update_traces(
        textposition='auto',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Valeur absolue: %{value:.2f}‰<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.05
        )
    )
    
    return fig.to_html(full_html=False)


def get_all_countries_with_migration():
    """Récupère la liste de tous les pays ayant des données de migration"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT DISTINCT c.name, c.location_code
        FROM country c
        JOIN fact_population fp ON c.location_code = fp.location_code
        WHERE fp.[NET MIGRATION RATE (PER 1.000 POPULATION)] IS NOT NULL
        ORDER BY c.name;
    """

    cursor.execute(query)
    results = [(row[0], row[1]) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    
    return results


def get_migration_rate_filtered(countries=None, year_start=None, year_end=None):
    """
    Récupère les données de migration avec filtres optionnels
    
    Args:
        countries (list): Liste des codes pays à filtrer (None = tous)
        year_start (int): Année de début (None = 1950)
        year_end (int): Année de fin (None = 2023)
        
    Returns:
        list of tuples: [(annee, taux, pays), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            fp.year,
            fp.[NET MIGRATION RATE (PER 1.000 POPULATION)] AS Taux,
            c.name
        FROM fact_population fp
        JOIN country c 
            ON fp.location_code = c.location_code
        WHERE 1=1
    """
    
    params = []
    
    # Filtre par pays
    if countries and len(countries) > 0:
        placeholders = ','.join(['?' for _ in countries])
        query += f" AND c.location_code IN ({placeholders})"
        params.extend(countries)
    
    # Filtre par année de début
    if year_start:
        query += " AND fp.year >= ?"
        params.append(year_start)
    
    # Filtre par année de fin
    if year_end:
        query += " AND fp.year <= ?"
        params.append(year_end)
    
    query += " ORDER BY fp.year DESC, c.name;"

    cursor.execute(query, params)
    results = cursor.fetchall()
    results_as_tuples = [tuple(row) for row in results]

    cursor.close()
    conn.close()
    
    return results_as_tuples
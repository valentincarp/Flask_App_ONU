# modules nécessaires
from models.db_utils import get_db_connection # pour se connecter à la base de données
import plotly.express as px # pour la création de graphiques interactifs
import pandas as pd         # pour la manipulation et l'analyse des données 

#GENRE HOMME/FEMME
# --- 1. AJOUTER CETTE NOUVELLE FONCTION ---
def get_available_years():
    """Récupère la liste de toutes les années disponibles dans la base"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # On sélectionne les années distinctes
    query = "SELECT DISTINCT year FROM fact_population ORDER BY year DESC"
    cursor.execute(query)
    # cursor.fetchall() renvoie des tuples (ex: [(2023,), (2022,), ...])
    # On transforme ça en une liste simple [2023, 2022, ...]
    years = [row[0] for row in cursor.fetchall()]
    conn.close()
    return years

# --- 2. MODIFIER LA FONCTION EXISTANTE (Ajout du paramètre year) ---
def get_gender_ratio(year):
    """Calcule le % d'hommes et de femmes pour chaque pays pour une année donnée"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Attention : on utilise un paramètre ? pour l'année dans le SQL pour la sécurité
    query = """
    SELECT 
        c.name AS nom_pays,
        fp.year AS annee,
        (fp."MALE POPULATION. AS OF 1 JULY (THOUSANDS)" / fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)") * 100 AS taux_hommes,
        (fp."FEMALE POPULATION. AS OF 1 JULY (THOUSANDS)" / fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)") * 100 AS taux_femmes
    FROM 
        fact_population fp
    JOIN 
        country c ON fp.location_code = c.location_code
    WHERE 
        fp.year = ?
    ORDER BY 
        c.name ASC;
    """
    cursor.execute(query, (year,)) # On passe l'année en paramètre
    results = cursor.fetchall()
    conn.close()
    return results

# --- 3. MODIFIER LA FONCTION DU GRAPHE (Ajout du paramètre year) ---
def generate_gender_ratio_plot(year):
    """Génère un graphe empilé Hommes/Femmes pour une année donnée"""
    
    # On passe l'année à la fonction de récupération des données
    data = get_gender_ratio(year)
    
    # Vérification de sécurité : si pas de données (ex: année invalide), on renvoie un message ou None
    if not data:
        return "<div>Aucune donnée disponible pour cette année.</div>"

    df = pd.DataFrame(data, columns=["Pays", "Année", "Hommes (%)", "Femmes (%)"])
    df = df.sort_values(by="Hommes (%)", ascending=False)
    
    fig = px.bar(
        df, 
        x="Pays", 
        y=["Hommes (%)", "Femmes (%)"],
        # Le titre se met à jour dynamiquement avec l'année
        title=f"Répartition Hommes / Femmes par pays en {year}",
        labels={"value": "Pourcentage (%)", "variable": "Sexe"},
        height=600, 
        color_discrete_map={"Hommes (%)": "#1f77b4", "Femmes (%)": "#d62728"}
    )
    
    fig.update_layout(
        yaxis=dict(range=[0, 100]), 
        xaxis={'categoryorder':'total descending'}, 
        legend_title_text='Genre',
        hovermode="x unified" 
    )
    
    return fig.to_html(full_html=False)
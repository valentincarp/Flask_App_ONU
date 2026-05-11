# models/export_utils.py
import pandas as pd

# Importation de TOUS les utils pour récupérer les données
from models import data_utils as du
from models import taux_utils as tu
from models import migration_models as mm
from models import life_utils as lu
from models import ratio_male_utils as rmu

def generate_csv_content(query_type, year=2023):
    """
    Génère le contenu CSV en fonction du type de page (query_type)
    """
    data = []
    columns = []

    # --- 1. POPULATION MONDIALE ---
    if query_type == 'world':
        data = du.get_world_population_by_year()
        columns = ["Année", "Hommes", "Femmes", "Total"]

    # --- 2. POPULATION PAR RÉGION ---
    elif query_type == 'region':
        data = du.get_population_by_region()
        columns = ["Région", "Année", "Population"]

    # --- 3. TOP 10 PAYS ---
    elif query_type == 'top10':
        data = du.get_top_10_countries() # Note: Vérifiez si cette fonction accepte une année
        columns = ["Année", "Pays", "Sous-région", "Région", "Continent", "Population"]

    # --- 4. RATIO HOMMES/FEMMES (Votre code existant) ---
    elif query_type == 'ratio':
        data = tu.get_gender_ratio(year)
        columns = ["Pays", "Année", "Taux Hommes (%)", "Taux Femmes (%)"]

    # --- 5. RATIO DÉTAILLÉ (Ratio Male) ---
    elif query_type == 'ratio_country':
        data = rmu.get_sex_ratio_data_country()
        # Adapter les colonnes selon ce que renvoie rmu
        columns = ["Pays", "Code", "Année", "Ratio", "Population"] 

    # --- 6. MIGRATION ---
    elif query_type == 'migration':
        # On récupère toutes les données sans filtre pour l'export
        data = mm.get_migration_rate_by_year()
        columns = ["Pays", "Année", "Taux de Migration"]

    # --- 7. ESPÉRANCE DE VIE ---
    elif query_type == 'lifeexp':
        # Pour l'export, on essaie de récupérer les données de l'année choisie
        # Attention : get_lifeexp_latest renvoie un DataFrame et une année
        try:
            df, y = lu.get_lifeexp_latest(year=year)
            # On convertit le DataFrame en liste pour l'export universel
            data = df.values.tolist()
            columns = ["Pays", f"Espérance de vie ({y})"]
        except:
            data = []

    # --- GESTION DES ERREURS ---
    if not data:
        return None
        
    # Création du DataFrame et conversion en CSV
    # On gère le cas où data est déjà un DataFrame (cas rare selon vos utils) ou une liste
    if isinstance(data, pd.DataFrame):
        df = data
    else:
        df = pd.DataFrame(data, columns=columns)

    # Export avec point-virgule pour Excel français
    return df.to_csv(index=False, sep=';', encoding='utf-8-sig')
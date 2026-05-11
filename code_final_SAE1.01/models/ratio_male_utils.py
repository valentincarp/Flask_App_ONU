
# ratio_male_utils.py
import pandas as pd
from models.db_utils import get_db_connection
import locale

# Configure la locale pour le formatage des nombres en français (utile pour afficher des nombres avec virgule)
locale.setlocale(locale.LC_NUMERIC, 'fr_FR.UTF-8')

def get_sex_ratio_data_country():
    """
    Récupère le ratio hommes/femmes à la naissance et dans la population totale par pays et par année.
    Retourne une liste de dictionnaires.
    """
    try:
        # Connexion à la base de données via une fonction utilitaire
        conn = get_db_connection()
        cursor = conn.cursor()

        # Requête SQL pour récupérer les données nécessaires
        query = """           
            SELECT  
                fp.location_code AS country_code,  
                c.name AS country_name, 
                fp.year AS year, 
                fp."SEX RATIO AT BIRTH (MALES PER 100 FEMALE BIRTHS)" AS sex_ratio_birth,  
                fp."POPULATION SEX RATIO. AS OF 1 JULY (MALES PER 100 FEMALES)" AS sex_ratio_population  
            FROM  
                fact_population fp  
            JOIN  
                country c  
            ON  
                fp.location_code = c.location_code;
        """

        # Exécution de la requête
        cursor.execute(query)
        results = cursor.fetchall()  # Récupère toutes les lignes

        # Récupère les noms des colonnes depuis la description du curseur
        columns = [desc[0] for desc in cursor.description]

        # Convertit chaque ligne en dictionnaire {colonne: valeur}
        data = [dict(zip(columns, row)) for row in results]


        # Ferme la connexion à la base
        conn.close()
        return data

    except Exception as e:
        # Gestion des erreurs : affiche le message et retourne une liste vide
        print(f"Erreur lors de la récupération des données : {e}")
        return []


def get_sex_ratio_data_subregion():
    """
    Récupère le ratio hommes/femmes à la naissance et dans la population totale par pays et par année.
    Retourne une liste de dictionnaires.
    """
    try:
        # Connexion à la base de données via une fonction utilitaire
        conn = get_db_connection()
        cursor = conn.cursor()

        # Requête SQL pour récupérer les données nécessaires
        query = """           
            SELECT  
                fp.location_code AS country_code,  
                s.name AS country_name, 
                fp.year AS year, 
                fp."SEX RATIO AT BIRTH (MALES PER 100 FEMALE BIRTHS)" AS sex_ratio_birth,  
                fp."POPULATION SEX RATIO. AS OF 1 JULY (MALES PER 100 FEMALES)" AS sex_ratio_population  
            FROM  
                fact_population fp  
            JOIN  
                subregion s  
            ON  
                fp.location_code = s.location_code;
        """

        # Exécution de la requête
        cursor.execute(query)
        results = cursor.fetchall()  # Récupère toutes les lignes

        # Récupère les noms des colonnes depuis la description du curseur
        columns = [desc[0] for desc in cursor.description]

        # Convertit chaque ligne en dictionnaire {colonne: valeur}
        data = [dict(zip(columns, row)) for row in results]


        # Ferme la connexion à la base
        conn.close()
        return data

    except Exception as e:
        # Gestion des erreurs : affiche le message et retourne une liste vide
        print(f"Erreur lors de la récupération des données : {e}")
        return []

def get_sex_ratio_data_region():
    """
    Récupère le ratio hommes/femmes à la naissance et dans la population totale par pays et par année.
    Retourne une liste de dictionnaires.
    """
    try:
        # Connexion à la base de données via une fonction utilitaire
        conn = get_db_connection()
        cursor = conn.cursor()

        # Requête SQL pour récupérer les données nécessaires
        query = """           
            SELECT  
                fp.location_code AS country_code,  
                r.name AS country_name, 
                fp.year AS year, 
                fp."SEX RATIO AT BIRTH (MALES PER 100 FEMALE BIRTHS)" AS sex_ratio_birth,  
                fp."POPULATION SEX RATIO. AS OF 1 JULY (MALES PER 100 FEMALES)" AS sex_ratio_population  
            FROM  
                fact_population fp  
            JOIN  
                region r  
            ON  
                fp.location_code = r.location_code;
        """

        # Exécution de la requête
        cursor.execute(query)
        results = cursor.fetchall()  # Récupère toutes les lignes

        # Récupère les noms des colonnes depuis la description du curseur
        columns = [desc[0] for desc in cursor.description]

        # Convertit chaque ligne en dictionnaire {colonne: valeur}
        data = [dict(zip(columns, row)) for row in results]


        # Ferme la connexion à la base
        conn.close()
        return data

    except Exception as e:
        # Gestion des erreurs : affiche le message et retourne une liste vide
        print(f"Erreur lors de la récupération des données : {e}")
        return []
# models/game_utils.py

"""
Module contenant les fonctions pour générer des questions aléatoires 
basées sur les données démographiques de la base de données.

Ce module interroge la base SQLite pour créer des questions de jeu
sur les populations et densités de différentes régions et pays.
"""

import random
from models.db_utils import get_db_connection

# Fonctions pour générer des questions aléatoires pour les jeux

def get_random_region_population():
    """
    Génère une question aléatoire sur la population d'une région du monde.
    
    La fonction :
    1. Choisit une année aléatoire entre 1950 et 2023
    2. Sélectionne une région aléatoire (Asie, Europe, Afrique, etc.)
    3. Récupère sa population pour cette année
    4. Convertit la population en millions d'habitants
    
    Returns:
        dict: Dictionnaire contenant :
            - question (str): Texte de la question à afficher
            - value (float): Valeur correcte à deviner (en millions)
            - unit (str): Unité de mesure ("millions d'habitants")
            - year (int): Année concernée
            - region (str): Nom de la région
            - tolerance (int): Marge d'erreur acceptée (±5 millions)
            - hint_min (int): Valeur minimale pour l'indice
            - hint_max (int): Valeur maximale pour l'indice
    
    Example:
        >>> question = get_random_region_population()
        >>> print(question['question'])
        "Quelle était la population de l'Asie en 1985 ?"
        >>> print(question['value'])
        2845.3  # En millions d'habitants
    """
    # Établir une connexion à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Générer une année aléatoire entre 1950 et 2023
    # Ces années correspondent aux données disponibles dans la base
    year = random.randint(1950, 2023)
    
    # Requête SQL pour obtenir la population d'une région aléatoire
    query = """
        SELECT
            r.name AS region_name,                                              -- Nom de la région
            SUM(fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000) AS total_population  -- Population totale
        FROM
            fact_population fp                                                  -- Table des faits de population
        JOIN
            region r ON fp.location_code = r.location_code                      -- Jointure avec la table des régions
        WHERE
            fp.year = ?                                                         -- Filtrer par année
        GROUP BY
            r.name                                                              -- Grouper par région
        ORDER BY
            RANDOM()                                                            -- Sélection aléatoire
        LIMIT 1;                                                                -- Prendre qu'une seule région
    """
    
    # Exécuter la requête avec l'année comme paramètre
    # Le '?' est un placeholder sécurisé pour éviter les injections SQL
    cursor.execute(query, (year,))
    
    # Récupérer le premier (et unique) résultat
    result = cursor.fetchone()
    
    # Fermer la connexion à la base de données
    conn.close()
    
    # Vérifier si un résultat a été trouvé
    if result:
        # Déstructurer le résultat : nom de la région et population
        region_name, population = result
        
        # Convertir la population de personnes en millions
        # Exemple : 245 000 000 habitants → 245.0 millions
        population_millions = population / 1_000_000
        
        # Retourner le dictionnaire avec toutes les informations
        return {
            'question': f"Quelle était la population de {region_name} en {year} ?",
            'value': round(population_millions, 1),    # Arrondir à 1 décimale
            'unit': 'millions d\'habitants',
            'year': year,
            'region': region_name,
            'tolerance': 5,      # Tolérance de plus ou moins 5 millions (réponses proches acceptées)
            'hint_min': 0,       # Indice : minimum possible
            'hint_max': 2000     # Indice : maximum possible (2 milliards)
        }
    else:
        # En cas d'erreur (aucun résultat trouvé), retourner une valeur par défaut
        return {
            'question': 'Erreur de chargement',
            'value': 0,
            'unit': 'millions',
            'tolerance': 0
        }


def get_random_country_population():
    """
    Génère une question aléatoire sur la population d'un pays.
    
    La fonction sélectionne uniquement des pays avec plus de 10 millions d'habitants
    pour éviter les petits pays difficiles à deviner.
    
    Returns:
        dict: Dictionnaire contenant les informations de la question
              (même structure que get_random_region_population)
    
    Example:
        >>> question = get_random_country_population()
        >>> print(question['question'])
        "Quelle était la population de la France en 2010 ?"
    """
    # Connexion à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Année aléatoire
    year = random.randint(1950, 2023)
    
    # Requête SQL pour sélectionner un pays aléatoire
    query = """
        SELECT
            c.name AS country_name,                                             -- Nom du pays
            fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000 AS population -- Population
        FROM
            fact_population fp
        JOIN
            country c ON fp.location_code = c.location_code                     -- Jointure avec la table des pays
        WHERE
            fp.year = ?                                                         -- Année spécifique
            AND fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000 > 10000000  -- Filtre : > 10 millions d'habitants
        ORDER BY
            RANDOM()                                                            -- Sélection aléatoire
        LIMIT 1;
    """
    
    # Exécution de la requête
    cursor.execute(query, (year,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        country_name, population = result
        
        # Conversion en millions
        population_millions = population / 1_000_000
        
        return {
            'question': f"Quelle était la population de {country_name} en {year} ?",
            'value': round(population_millions, 1),
            'unit': 'millions d\'habitants',
            'year': year,
            'country': country_name,
            'tolerance': 2,      # Tolérance plus stricte pour les pays (±2 millions)
            'hint_min': 0,
            'hint_max': 1500     # Maximum 1,5 milliard (pour éviter de donner trop d'indice)
        }
    else:
        return {
            'question': 'Erreur de chargement',
            'value': 0,
            'unit': 'millions',
            'tolerance': 0
        }


def get_random_europe_density():
    """
    Génère une question aléatoire sur la densité de population d'un pays européen.
    
    Utilise toujours l'année 2023 (données les plus récentes).
    Exclut les micro-États (Monaco, Vatican, etc.) qui ont des densités extrêmes.
    
    Returns:
        dict: Dictionnaire contenant les informations de la question
              avec l'unité en habitants/km²
    
    Example:
        >>> question = get_random_europe_density()
        >>> print(question['question'])
        "Quelle est la densité de population de l'Allemagne en 2023 ?"
        >>> print(question['value'])
        237.4  # habitants par km²
    """
    # Connexion à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Utiliser l'année la plus récente disponible
    year = 2023
    
    # Requête SQL pour sélectionner un pays européen
    query = """
        SELECT
            c.name AS country_name,                                             -- Nom du pays
            fp."POPULATION DENSITY. AS OF 1 JULY (PERSONS PER SQUARE KM)" AS density  -- Densité de population
        FROM
            fact_population fp
        JOIN
            country c ON fp.location_code = c.location_code                     -- Jointure pays
        JOIN
            subregion s ON c.parent_code = s.location_code                      -- Jointure sous-région
        JOIN
            region r ON s.parent_code = r.location_code                         -- Jointure région
        WHERE
            r.name = 'Europe'                                                   -- Filtrer uniquement l'Europe
            AND fp.year = ?                                                     -- Année 2023
            AND c.name NOT IN ('Monaco', 'Gibraltar', 'Holy See', 'Malta', 'San Marino', 'Guernsey', 'Jersey')  -- Exclure les micro-États
        ORDER BY
            RANDOM()                                                            -- Sélection aléatoire
        LIMIT 1;
    """
    
    # Exécution de la requête
    cursor.execute(query, (year,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        country_name, density = result
        
        return {
            'question': f"Quelle est la densité de population de {country_name} en {year} ?",
            'value': round(density, 1),           # Arrondir la densité à 1 décimale
            'unit': 'habitants/km²',              # Unité différente pour la densité
            'year': year,
            'country': country_name,
            'tolerance': 5,                       # Tolérance de ±5 habitants/km²
            'hint_min': 0,
            'hint_max': 500                       # Maximum 500 hab/km² (densités extrêmes exclues)
        }
    else:
        return {
            'question': 'Erreur de chargement',
            'value': 0,
            'unit': 'hab/km²',
            'tolerance': 0
        }


def get_world_population_year():
    """
    Génère une question sur la population mondiale totale pour une année donnée.
    
    Cette fonction additionne la population de toutes les régions du monde
    pour obtenir la population mondiale totale, puis la convertit en milliards.
    
    Returns:
        dict: Dictionnaire contenant les informations de la question
              avec l'unité en milliards d'habitants
    
    Example:
         question = get_world_population_year()
         print(question['question'])
        "Quelle était la population mondiale en 1975 ?"
         print(question['value'])
        4.07  # En milliards d'habitants
    """
    # Connexion à la base de données
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Année aléatoire
    year = random.randint(1950, 2023)
    
    # Requête SQL pour calculer la population mondiale
    query = """
        SELECT
            SUM(fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000) AS total_population  -- Somme de toutes les populations
        FROM
            fact_population fp
        WHERE
            fp.location_code IN (SELECT location_code FROM region)              -- Seulement les régions (pas les pays)
            AND fp.year = ?;                                                    -- Année spécifique
    """
    
    # Exécution de la requête
    cursor.execute(query, (year,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        population = result[0]
        
        # Conversion en milliards (pour la population mondiale)
        # Exemple : 7 800 000 000 habitants devient  7.8 milliards
        population_billions = population / 1_000_000_000
        
        return {
            'question': f"Quelle était la population mondiale en {year} ?",
            'value': round(population_billions, 2),   # Arrondir à 2 décimales pour les milliards
            'unit': 'milliards d\'habitants',
            'year': year,
            'tolerance': 0.1,                         # Tolérance de ±0.1 milliard (100 millions)
            'hint_min': 0,
            'hint_max': 10                            # Maximum 10 milliards
        }
    else:
        return {
            'question': 'Erreur de chargement',
            'value': 0,
            'unit': 'milliards',
            'tolerance': 0
        }
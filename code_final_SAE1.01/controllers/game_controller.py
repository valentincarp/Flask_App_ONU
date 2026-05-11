from flask import Blueprint, render_template, request, session
import random
from models import game_utils as gu

# Créer un Blueprint pour gérer les routes du jeu
# Un Blueprint permet d'organiser les routes de manière modulaire
game = Blueprint('game', __name__)

@game.route('/game')
def index():
    """
    Route principale du jeu du plus ou moins démographique.
    
    Cette fonction gère :
    - L'initialisation d'une nouvelle partie
    - La validation des propositions de l'utilisateur
    - La gestion de l'historique des tentatives
    - L'affichage des messages de feedback
    
    Paramètres URL :
        game (str): Type de jeu ('region_population', 'country_population', 'europe_density')
        guess (float): Proposition de l'utilisateur
        new (str): '1' pour démarrer une nouvelle partie
    
    Returns:
        Template HTML avec les données du jeu
    """
    
    # Récupérer le type de jeu depuis les paramètres URL
    # Par défaut : 'region_population' (population par région)
    game_type = request.args.get('game', 'region_population')
    
    # Vérifier si c'est une nouvelle partie ou si aucune partie n'existe
    if 'secret_data' not in session or request.args.get('new') == '1':
        # Récupérer une question aléatoire selon le type de jeu sélectionné
        if game_type == 'region_population':
            # Question sur la population d'une région (Asie, Europe, etc.)
            secret_data = gu.get_random_region_population()
        elif game_type == 'country_population':
            # Question sur la population d'un pays
            secret_data = gu.get_random_country_population()
        elif game_type == 'europe_density':
            # Question sur la densité de population d'un pays européen
            secret_data = gu.get_random_europe_density()
        else:
            # Type inconnu : utiliser le mode région par défaut
            secret_data = gu.get_random_region_population()
        
        # Stocker les données de la partie dans la session Flask
        # La session permet de conserver les données entre les requêtes HTTP
        session['secret_data'] = secret_data          # Données de la question (valeur secrète, texte, etc.)
        session['attempts'] = 0                       # Compteur de tentatives
        session['max_attempts'] = 7                   # Nombre maximum d'essais autorisés
        session['game_over'] = False                  # Indicateur de fin de partie
        session['won'] = False                        # Indicateur de victoire
        session['history'] = []                       # Historique des tentatives
        session['game_type'] = game_type              # Type de jeu en cours
    
    # Récupérer les données secrètes (question et valeur à deviner)
    secret_data = session.get('secret_data', {})
    
    # Préparer un dictionnaire avec toutes les données à envoyer au template
    data = {
        'attempts': session.get('attempts', 0),           # Nombre de tentatives effectuées
        'max_attempts': session.get('max_attempts', 7),   # Nombre maximum d'essais
        'game_over': session.get('game_over', False),     # La partie est-elle terminée ?
        'won': session.get('won', False),                 # L'utilisateur a-t-il gagné ?
        'history': session.get('history', []),            # Liste des tentatives précédentes
        'message': None,                                  # Message de feedback (sera rempli si proposition)
        'guess': None,                                    # Dernière proposition de l'utilisateur
        'question': secret_data.get('question', ''),      # Texte de la question
        'unit': secret_data.get('unit', ''),              # Unité de mesure (millions, hab/km², etc.)
        'year': secret_data.get('year', ''),              # Année concernée par la question
        'hint_min': secret_data.get('hint_min', 0),       # Valeur minimale de l'indice
        'hint_max': secret_data.get('hint_max', 1000)     # Valeur maximale de l'indice
    }
    
    # Vérifier si l'utilisateur a soumis une proposition
    if request.args.get('guess'):
        try:
            # Convertir la proposition en nombre décimal
            guess = float(request.args.get('guess'))
            data['guess'] = guess
            
            # Traiter la proposition uniquement si la partie n'est pas terminée
            if not session['game_over']:
                # Incrémenter le compteur de tentatives
                session['attempts'] += 1
                
                # Récupérer la valeur secrète à deviner
                secret_value = secret_data['value']
                
                # Récupérer la tolérance (marge d'erreur acceptée)
                # Par exemple : ±5 millions pour une population
                tolerance = secret_data.get('tolerance', 0)
                
                # Vérifier si la réponse est correcte (avec tolérance)
                # abs() calcule la valeur absolue de la différence
                if abs(guess - secret_value) <= tolerance:
                    # VICTOIRE : La réponse est dans la marge de tolérance
                    session['won'] = True
                    session['game_over'] = True
                    data['message'] = f"Bravo ! La réponse était {secret_value:.1f} {secret_data['unit']}. Vous avez trouvé en {session['attempts']} essai(s) !"
                    data['won'] = True
                    
                elif session['attempts'] >= session['max_attempts']:
                    # DÉFAITE : Nombre maximum de tentatives atteint
                    session['game_over'] = True
                    data['message'] = f"Perdu ! La réponse était {secret_value:.1f} {secret_data['unit']}. Vous avez épuisé vos {session['max_attempts']} essais."
                    
                elif guess < secret_value - tolerance:
                    # INDICE : La valeur à trouver est plus grande
                    data['message'] = "📈 C'est plus !"
                    
                else:
                    # INDICE : La valeur à trouver est plus petite
                    data['message'] = "📉 C'est moins !"
                
                # Créer une entrée pour l'historique des tentatives
                if not session['won']:
                    # Si pas encore gagné : afficher l'indice "Plus" ou "Moins"
                    history_entry = {
                        'attempt': session['attempts'],                           # Numéro de la tentative
                        'guess': f"{guess:.1f}",                                  # Valeur proposée (formatée)
                        'hint': 'Plus' if guess < secret_value - tolerance else 'Moins'  # Indice
                    }
                else:
                    # Si gagné : afficher "Trouvé !"
                    history_entry = {
                        'attempt': session['attempts'],
                        'guess': f"{guess:.1f}",
                        'hint': 'Trouvé !'
                    }
                
                # Ajouter l'entrée à l'historique dans la session
                session['history'] = session.get('history', []) + [history_entry]
                
                # Mettre à jour les données à envoyer au template
                data['history'] = session['history']
                data['attempts'] = session['attempts']
                data['game_over'] = session['game_over']
                
        except ValueError:
            # Gestion d'erreur : si la conversion en float échoue
            data['message'] = "Veuillez entrer un nombre valide."
    
    # Déterminer le titre selon le type de jeu
    if game_type == 'region_population':
        title = "Jeu - Population par région"
    elif game_type == 'country_population':
        title = "Jeu - Population par pays"
    elif game_type == 'europe_density':
        title = "Jeu - Densité européenne"
    else:
        title = "Jeu démographique"
    
    # Retourner le template HTML avec toutes les données
    return render_template(
        'game.html',         # Nom du template à utiliser
        title=title,         # Titre de la page
        game_type=game_type, # Type de jeu actuel
        data=data            # Dictionnaire contenant toutes les données du jeu
    )

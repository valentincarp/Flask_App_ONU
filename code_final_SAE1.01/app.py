# app.py

# Programme principal pour lancer l'application Flask

# Importer les modules nécessaires
from flask import Flask                                 # pour créer l'application Flask
from controllers.main_controller import main            # importer le Blueprint principal 
from controllers.dashboard_controller import dashboard  # importer le Blueprint du tableau de bord
from controllers.forecast_controller import forecast_bp # importer les prévisions
from controllers.esperence_vie_controller import life
from controllers.game_controller import game
from controllers.migration_controllers import migration
from controllers.ratio_controller import ratio_bp
from controllers.ratio_male_controller import ratio_male 
from controllers.export_controller import export_bp
# Créer l'application Flask
app = Flask(__name__)

# Nécessaire pour que le Jeu (game_controller) fonctionne avec les "sessions"
app.secret_key = 'votre_cle_secrete_aleatoire_et_securisee'
# Enregistrer les Blueprints
# Le Blueprint 'main' gère la route principale de l'application
app.register_blueprint(main)
# Le Blueprint 'dashboard' gère la route du tableau de bord
app.register_blueprint(dashboard)

app.register_blueprint(forecast_bp) # gère la route 

app.register_blueprint(life)       # Route: /life
app.register_blueprint(game)       # Route: /game
app.register_blueprint(migration)  # Route: /migration
app.register_blueprint(ratio_bp)   # Route: /ratio
app.register_blueprint(ratio_male) # Route: /ratio_male
app.register_blueprint(export_bp)
# Lancer l'application Flask
if __name__ == '__main__':
    # Lancer l'application en mode debug sur localhost via le port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)

    # Après avoir lancé l'application, accédez à l'URL suivante dans un navigateur web :
    # http://127.0.0.1:5000

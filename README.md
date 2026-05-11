# Analyse Démographique Mondiale — SAE 1.01

Application web interactive d'exploration et de visualisation 
des données démographiques mondiales (ONU, 1950–2023).

Projet réalisé en équipe dans le cadre du BUT Informatique 
à l'IUT de Créteil-Vitry.

## Fonctionnalités

- **Population mondiale** — évolution historique et prévisions sur 30 ans
- **Régions** — comparaison par région et sous-région
- **Espérance de vie** — tableau, graphique ou carte choroplèthe par pays et par année
- **Migration** — flux migratoires par pays (tableau + camembert interactif)
- **Taux H/F** — répartition hommes/femmes par pays de 1950 à 2023
- **Ratio H/F** — diagramme circulaire avec filtres géographiques
- **Jeu** — "Plus ou Moins" sur les données démographiques
- **Export CSV** — téléchargement des données depuis chaque page

## Technologies

- Python / Flask (architecture MVC)
- SQLite
- Pandas
- Plotly
- Jinja2
- DataTables

## Lancer le projet

```bash
pip install -r requirements.txt
python app.py
```

Ouvrir ensuite http://127.0.0.1:5000 dans un navigateur.

## Structure

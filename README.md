# Analyse Démographique Mondiale — SAE 1.01

Application web interactive d'exploration et de visualisation 
des données démographiques mondiales (ONU, 1950–2023).

Projet réalisé en équipe dans le cadre du BUT Informatique 
à l'IUT de Créteil-Vitry.

## Fonctionnalités

- **Population mondiale** — évolution historique et prévisions sur 30 ans
  <img width="1470" height="823" alt="Capture d’écran 2026-05-11 à 16 22 31" src="https://github.com/user-attachments/assets/26feb95d-59c1-4b86-bdfa-08cdbde2565f" />
  
- **Régions** — comparaison par région et sous-région
  <img width="1470" height="823" alt="Capture d’écran 2026-05-11 à 16 25 49" src="https://github.com/user-attachments/assets/e9c86481-1e53-457d-9ba0-2f0b2522f8f1" />

- **Espérance de vie** — tableau, graphique ou carte choroplèthe par pays et par année
  <img width="1470" height="827" alt="Capture d’écran 2026-05-11 à 16 26 09" src="https://github.com/user-attachments/assets/04208078-0cca-49bd-97fa-ec6ea7368c04" />

- **Migration** — flux migratoires par pays (tableau + camembert interactif)
  <img width="1470" height="827" alt="Capture d’écran 2026-05-11 à 16 26 20" src="https://github.com/user-attachments/assets/d847451d-1e24-401d-b1e2-b24e391ee59e" />

- **Taux H/F** — répartition hommes/femmes par pays de 1950 à 2023
  <img width="1470" height="823" alt="Capture d’écran 2026-05-11 à 16 22 42" src="https://github.com/user-attachments/assets/311b9033-009f-4480-9d9f-3ac7661ea197" />

- **Ratio H/F** — diagramme circulaire avec filtres géographiques
  <img width="1470" height="823" alt="Capture d’écran 2026-05-11 à 16 25 04" src="https://github.com/user-attachments/assets/f3c34134-a61e-4af0-9562-f06871c3499c" />

- **Jeu** — "Plus ou Moins" sur les données démographiques
  <img width="1470" height="823" alt="Capture d’écran 2026-05-11 à 16 22 56" src="https://github.com/user-attachments/assets/f73eefdf-c86e-446d-8208-cb632c611549" />

- **Export CSV** — téléchargement des données depuis chaque page
  <img width="291" height="66" alt="Capture d’écran 2026-05-11 à 16 25 59" src="https://github.com/user-attachments/assets/4e93702d-01d2-49d2-8858-2b30047e7815" />

## Technologies

- Python / Flask (architecture MVC)
- SQLite
- Pandas
- Plotly
- Jinja2
- DataTables

## Lancer le projet

python app.py

Ouvrir ensuite http://127.0.0.1:5000 dans un navigateur.

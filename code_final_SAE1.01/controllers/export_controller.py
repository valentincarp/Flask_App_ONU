# controllers/export_controller.py
from flask import Blueprint, request, Response
from models import export_utils as eu

# C'est cette ligne qui manquait ou était mal écrite
export_bp = Blueprint('export', __name__)

@export_bp.route('/download_csv')
def download_csv():
    # 1. Récupérer les paramètres
    query_type = request.args.get('query', 'world')
    try:
        year = int(request.args.get('year', 2023))
    except ValueError:
        year = 2023

    # 2. Générer le CSV
    csv_content = eu.generate_csv_content(query_type, year)

    if not csv_content:
        return "Erreur : Pas de données", 404

    # 3. Renvoyer le fichier
    filename = f"export_{query_type}_{year}.csv"
    
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={
            "Content-disposition": f"attachment; filename={filename}"
        }
    )
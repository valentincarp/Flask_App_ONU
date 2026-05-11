
from flask import Blueprint, request, render_template
from models import life_utils as lu

life = Blueprint("life", __name__, url_prefix="/life")


@life.route("/", methods=["GET"])
def life_home():
    view_type = request.args.get("view", "table")
    year = request.args.get("year", type=int)
    country = (request.args.get("country") or "").strip() or None

    title = "Espérance de vie"
    headers, data, plot_html = [], [], None
    error_msg = None

    try:
        if view_type == "graph":
            plot_html = lu.generate_lifeexp_plot(country=country)

        elif view_type == "map":
            plot_html = lu.generate_lifeexp_map(year=year, country=country)

        else:
            df, y = lu.get_lifeexp_latest(year=year, country=country)
            headers = ["Pays", f"Espérance de vie (années) – {y}"]
            data = df.values.tolist()

    except ValueError as e:
        # Exemple : "Pays inconnu: ..."
        error_msg = str(e)

    return render_template(
        "life.html",
        title=title,
        headers=headers,
        data=data,
        plot_html=plot_html,
        query_type="lifeexp",
        view_type=view_type,
        error_msg=error_msg,
    )

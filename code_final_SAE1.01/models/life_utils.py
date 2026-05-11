
import json
from typing import Optional, Tuple

import folium
import pandas as pd
import plotly.express as px

import config
from models.db_utils import get_db_connection


COL_EV = "LIFE EXPECTANCY AT BIRTH. BOTH SEXES (YEARS)"


def resolve_location_code(country: str) -> Tuple[str, str]:
    """
    Retourne (location_code, nom_officiel) à partir d'un nom de pays.
    Recherche : exact (insensible à la casse) puis LIKE.
    Lève ValueError si introuvable.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT location_code, name FROM country WHERE LOWER(name)=LOWER(?) LIMIT 1",
        (country,),
    )
    row = cur.fetchone()

    if not row:
        cur.execute(
            "SELECT location_code, name FROM country WHERE LOWER(name) LIKE LOWER(?) LIMIT 1",
            (f"%{country}%",),
        )
        row = cur.fetchone()

    conn.close()

    if not row:
        raise ValueError(f"Pays inconnu: {country}")

    return row[0], row[1]


def get_lifeexp_latest(year: Optional[int] = None, country: Optional[str] = None):
    """
    Retourne (DataFrame(country, life_expectancy), année_utilisée).
    Si country est renseigné -> retourne uniquement ce pays (si existant).
    """
    conn = get_db_connection()
    cur = conn.cursor()

    if year is None:
        cur.execute(f'SELECT MAX(year) FROM fact_population WHERE "{COL_EV}" IS NOT NULL')
        year = int(cur.fetchone()[0])

    if country and country.strip():
        loc, _official_name = resolve_location_code(country)

        cur.execute(
            f"""
            SELECT c.name AS country,
                   fp."{COL_EV}" AS life_expectancy
            FROM fact_population fp
            JOIN country c ON fp.location_code = c.location_code
            WHERE fp.year = ?
              AND fp.location_code = ?
              AND fp."{COL_EV}" IS NOT NULL
            """,
            (year, loc),
        )
    else:
        cur.execute(
            f"""
            SELECT c.name AS country,
                   fp."{COL_EV}" AS life_expectancy
            FROM fact_population fp
            JOIN country c ON fp.location_code = c.location_code
            WHERE fp.year = ?
              AND fp."{COL_EV}" IS NOT NULL
            ORDER BY life_expectancy DESC, country ASC
            """,
            (year,),
        )

    rows = cur.fetchall()
    conn.close()

    return pd.DataFrame(rows, columns=["country", "life_expectancy"]), year


def get_lifeexp_over_time(country: Optional[str] = None):
    """
    Série temporelle monde (location_code='900') ou d'un pays.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    if country is None or country.strip() == "":
        cur.execute(
            f"""
            SELECT year, "{COL_EV}" AS life_expectancy
            FROM fact_population
            WHERE location_code='900'
              AND "{COL_EV}" IS NOT NULL
            ORDER BY year
            """
        )
        rows = cur.fetchall()
        conn.close()
        return pd.DataFrame(rows, columns=["year", "life_expectancy"])

    loc, _official_name = resolve_location_code(country)

    cur.execute(
        f"""
        SELECT year, "{COL_EV}" AS life_expectancy
        FROM fact_population
        WHERE location_code=?
          AND "{COL_EV}" IS NOT NULL
        ORDER BY year
        """,
        (loc,),
    )

    rows = cur.fetchall()
    conn.close()
    return pd.DataFrame(rows, columns=["year", "life_expectancy"])


def generate_lifeexp_plot(country: Optional[str] = None) -> str:
    df = get_lifeexp_over_time(country)

    if df.empty:
        return "<div><em>Aucune donnée d'espérance de vie.</em></div>"

    title = (
        f"Évolution de l'espérance de vie – {country}"
        if country
        else "Évolution mondiale de l'espérance de vie"
    )

    fig = px.line(
        df,
        x="year",
        y="life_expectancy",
        markers=True,
        title=title,
        labels={"year": "Année", "life_expectancy": "Années"},
    )
    fig.update_layout(hovermode="x unified", template="plotly_white")
    return fig.to_html(full_html=False)


def generate_lifeexp_map(year: Optional[int] = None, country: Optional[str] = None) -> str:
    """
    Carte choroplèthe.
    Si country est renseigné => seule la ligne de ce pays est utilisée
    (le reste apparaît en gris).
    """
    df, y = get_lifeexp_latest(year=year, country=country)

    if df.empty:
        return "<div><em>Pas de données pour la carte.</em></div>"

    with open(config.GEOJSON_10M, "r", encoding="utf-8") as f:
        gj = json.load(f)

    m = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="cartodbpositron",
        width="100%",
        height="450px",
    )

    folium.Choropleth(
        geo_data=gj,
        data=df,
        columns=["country", "life_expectancy"],
        key_on="feature.properties.NAME_ENGL",  # <-- adapte si ton GeoJSON utilise une autre clé
        fill_color="YlGnBu",
        fill_opacity=0.75,
        line_opacity=0.2,
        nan_fill_color="lightgray",
        legend_name=f"Espérance de vie (années) – {y}",
    ).add_to(m)

    return m._repr_html_()

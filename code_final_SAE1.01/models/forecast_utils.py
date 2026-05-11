# models/forecast_utils.py

import pandas as pd
import plotly.express as px
from models.db_utils import get_db_connection
from models import data_utils as du 

# --- A. STATISTIQUES VITALES (HISTORIQUE 1950-2023) ---
def get_vital_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Requête pour l'historique réel
    query = """
        SELECT 
            fp.year,
            AVG(fp."CRUDE BIRTH RATE (BIRTHS PER 1.000 POPULATION)") as birth_rate,
            AVG(fp."CRUDE DEATH RATE (DEATHS PER 1.000 POPULATION)") as death_rate
        FROM fact_population fp
        WHERE fp.location_code IN (SELECT location_code FROM region)
        GROUP BY fp.year
        ORDER BY fp.year;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def generate_vital_history_plot():
    data = get_vital_history()
    df = pd.DataFrame(data, columns=["Année", "Taux de Natalité", "Taux de Mortalité"])
    
    fig = px.line(df, x="Année", y=["Taux de Natalité", "Taux de Mortalité"],
                  title="Historique : Natalité vs Mortalité (1950-2023)",
                  labels={"value": "Taux (‰)", "variable": "Indicateur"},
                  color_discrete_map={"Taux de Natalité": "#2ca02c", "Taux de Mortalité": "#d62728"})
    fig.update_layout(hovermode="x unified")
    return fig.to_html(full_html=False)


# --- B. OUTILS PRÉVISIONS (Régression Linéaire) ---
def calculate_linear_prediction(df, year_col, value_col, years_ahead=30):
    if len(df) < 2: return pd.DataFrame()
    n = len(df)
    sum_x = df[year_col].sum()
    sum_y = df[value_col].sum()
    sum_xy = sum(df[year_col] * df[value_col])
    sum_x2 = sum(df[year_col] ** 2)
    denom = (n * sum_x2 - sum_x**2)
    if denom == 0: return pd.DataFrame()
    a = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - a * sum_x) / n
    last_year = df[year_col].max()
    future_years = list(range(last_year + 1, last_year + years_ahead + 1))
    preds = [a * y + b for y in future_years]
    return pd.DataFrame({year_col: future_years, value_col: preds, 'Type': 'Prévision'})


# --- C. FONCTIONS DE PRÉVISION ---

# 1. Monde
def get_world_forecast():
    raw_data = du.get_world_population_by_year()
    df = pd.DataFrame(raw_data, columns=["year", "male", "female", "total"])
    df_pred = calculate_linear_prediction(df, "year", "total")
    history = df[['year', 'total']].copy()
    history['Type'] = 'Historique'
    return pd.concat([history, df_pred]).values.tolist()

def generate_world_forecast_plot():
    data = get_world_forecast()
    df = pd.DataFrame(data, columns=["Année", "Population", "Type"])
    fig = px.line(df, x="Année", y="Population", color="Type", title="Prévision Monde (30 ans)",
                  color_discrete_map={"Historique": "blue", "Prévision": "orange"})
    fig.update_traces(patch={"line": {"dash": "dot"}}, selector={"name": "Prévision"})
    return fig.to_html(full_html=False)

# 2. Régions
def get_region_forecast():
    raw_data = du.get_population_by_region()
    df = pd.DataFrame(raw_data, columns=["region", "year", "population"])
    final_df = pd.DataFrame()
    for region in df['region'].unique():
        df_reg = df[df['region'] == region]
        df_hist = df_reg.copy()
        df_hist['Type'] = 'Historique'
        df_pred = calculate_linear_prediction(df_reg, "year", "population")
        if not df_pred.empty:
            df_pred['region'] = region
            final_df = pd.concat([final_df, df_hist, df_pred])
        else:
            final_df = pd.concat([final_df, df_hist])
    return final_df.values.tolist()

def generate_region_forecast_plot():
    data = get_region_forecast()
    df = pd.DataFrame(data, columns=["Région", "Année", "Population", "Type"])
    fig = px.line(df, x="Année", y="Population", color="Région", line_dash="Type",
                  title="Prévisions par Région", line_dash_map={"Historique": "solid", "Prévision": "dot"})
    return fig.to_html(full_html=False)

# 3. Europe
def get_europe_forecast():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT fp.year, SUM(fp."TOTAL POPULATION. AS OF 1 JULY (THOUSANDS)" * 1000) as pop,
               AVG(fp."POPULATION DENSITY. AS OF 1 JULY (PERSONS PER SQUARE KM)") as density
        FROM fact_population fp
        JOIN country c ON fp.location_code = c.location_code
        JOIN subregion s ON c.parent_code = s.location_code
        JOIN region r ON s.parent_code = r.location_code
        WHERE r.name = 'Europe' GROUP BY fp.year ORDER BY fp.year
    """
    cursor.execute(query)
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=["year", "population", "density"])
    pred_pop = calculate_linear_prediction(df, "year", "population")
    pred_dens = calculate_linear_prediction(df, "year", "density")
    pred_merged = pd.merge(pred_pop, pred_dens, on=["year", "Type"]).rename(columns={"value_x": "population", "value_y": "density"})
    history = df.copy()
    history['Type'] = 'Historique'
    return pd.concat([history, pred_merged]).values.tolist()

def generate_europe_forecast_plot():
    data = get_europe_forecast()
    df = pd.DataFrame(data, columns=["Année", "Population", "Densité", "Type"])
    fig = px.line(df, x="Année", y="Population", color="Type", title="Prévision Europe",
                  color_discrete_map={"Historique": "blue", "Prévision": "orange"})
    fig.update_traces(patch={"line": {"dash": "dot"}}, selector={"name": "Prévision"})
    return fig.to_html(full_html=False)

# 4. Prévision Vitales
def get_vital_forecast():
    raw_data = get_vital_history() # On utilise l'historique défini plus haut
    df = pd.DataFrame(raw_data, columns=["year", "birth", "death"])
    pred_birth = calculate_linear_prediction(df, "year", "birth")
    pred_death = calculate_linear_prediction(df, "year", "death")
    pred_merged = pd.merge(pred_birth, pred_death, on=["year", "Type"]).rename(columns={"value_x": "birth", "value_y": "death"})
    history = df.copy()
    history['Type'] = 'Historique'
    return pd.concat([history, pred_merged]).values.tolist()

def generate_vital_forecast_plot():
    data = get_vital_forecast()
    df = pd.DataFrame(data, columns=["Année", "Taux Natalité", "Taux Mortalité", "Type"])
    fig = px.line(df, x="Année", y=["Taux Natalité", "Taux Mortalité"], 
                  color_discrete_map={"Taux Natalité": "green", "Taux Mortalité": "red"},
                  line_dash="Type", line_dash_map={"Historique": "solid", "Prévision": "dot"},
                  title="Prévision Natalité vs Mortalité")
    return fig.to_html(full_html=False)
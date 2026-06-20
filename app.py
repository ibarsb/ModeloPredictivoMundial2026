import streamlit as st
import numpy as np
from scipy.stats import poisson
import pandas as pd

# Configuración de página ancha y título
st.set_page_config(layout="wide", page_title="Predictor Mundial 2026", page_icon="🏆")

# 1. BASE DE DATOS: LAS 48 SELECCIONES CLASIFICADAS
teams_db = {
    "CONMEBOL": {
        "Argentina": {"atk": 2.15, "def": 0.65},
        "Brasil": {"atk": 1.95, "def": 0.75},
        "Uruguay": {"atk": 1.85, "def": 0.80},
        "Colombia": {"atk": 1.70, "def": 0.85},
        "Ecuador": {"atk": 1.45, "def": 0.80},
        "Paraguay": {"atk": 1.10, "def": 0.90},
        "Venezuela": {"atk": 1.25, "def": 1.05},
        "Chile": {"atk": 1.20, "def": 1.10},
    },
    "UEFA": {
        "Francia": {"atk": 2.10, "def": 0.70},
        "España": {"atk": 2.00, "def": 0.68},
        "Inglaterra": {"atk": 1.95, "def": 0.72},
        "Portugal": {"atk": 1.90, "def": 0.78},
        "Alemania": {"atk": 1.85, "def": 0.85},
        "Países Bajos": {"atk": 1.75, "def": 0.82},
        "Italia": {"atk": 1.50, "def": 0.75},
        "Croacia": {"atk": 1.45, "def": 0.88},
        "Bélgica": {"atk": 1.60, "def": 0.95},
        "Dinamarca": {"atk": 1.40, "def": 0.90},
        "Suiza": {"atk": 1.35, "def": 0.92},
        "Austria": {"atk": 1.40, "def": 0.95},
        "Turquía": {"atk": 1.45, "def": 1.15},
        "Ucrania": {"atk": 1.30, "def": 1.00},
        "Polonia": {"atk": 1.25, "def": 1.10},
        "Serbia": {"atk": 1.35, "def": 1.20},
    },
    "CONCACAF": {
        "Estados Unidos": {"atk": 1.55, "def": 0.90},
        "México": {"atk": 1.40, "def": 0.95},
        "Canadá": {"atk": 1.45, "def": 1.00},
        "Panamá": {"atk": 1.15, "def": 1.10},
        "Costa Rica": {"atk": 1.05, "def": 1.15},
        "Jamaica": {"atk": 1.10, "def": 1.12},
    },
    "CAF (África)": {
        "Marruecos": {"atk": 1.65, "def": 0.75},
        "Senegal": {"atk": 1.55, "def": 0.85},
        "Nigeria": {"atk": 1.60, "def": 1.05},
        "Egipto": {"atk": 1.35, "def": 0.90},
        "Argelia": {"atk": 1.40, "def": 1.00},
        "Túnez": {"atk": 1.10, "def": 0.95},
        "Costa de Marfil": {"atk": 1.45, "def": 1.00},
        "Camerún": {"atk": 1.30, "def": 1.05},
        "Malí": {"atk": 1.15, "def": 0.98},
    },
    "AFC (Asia)": {
        "Japón": {"atk": 1.60, "def": 0.85},
        "Corea del Sur": {"atk": 1.50, "def": 0.95},
        "Irán": {"atk": 1.35, "def": 0.90},
        "Australia": {"atk": 1.30, "def": 0.92},
        "Arabia Saudita": {"atk": 1.15, "def": 1.05},
        "Qatar": {"atk": 1.20, "def": 1.15},
        "Irak": {"atk": 1.10, "def": 1.10},
        "Uzbekistán": {"atk": 1.05, "def": 1.00},
    },
    "OFC (Oceanía)": {
        "Nueva Zelanda": {"atk": 1.00, "def": 1.20}
    }
}

# Unificar todo en un solo diccionario plano
todos_los_equipos = {}
for conf, equipos in teams_db.items():
    for nombre, stats in equipos.items():
        todos_los_equipos[nombre] = stats

st.title("🏆 Mundial 2026 — Predictor Avanzado Pro")

st.caption("🚀 Desarrollado por **Ibars Brian** | Proyecto Final de Ciencia de Datos")

st.markdown("Sistema de simulación Monte Carlo basado en Poisson bivariado con ajuste Dixon-Coles.")

# --- MEJORA 1: EXPANDER METODOLÓGICO PARA LA ENTREGA DE LA TAREA ---
with st.expander("🤓 Ver Ficha Técnica y Metodología Científica del Modelo"):
    st.markdown("""
    **Sustentación del Modelo de Datos:**
    * **Distribución de Poisson:** Utilizada para modelar la probabilidad de eventos independientes en un intervalo de tiempo fijo (goles en 90'). La tasa media ($\lambda$) de cada equipo se calcula dinámicamente multiplicando el factor ofensivo propio por el defensivo del rival.
    * **Ajuste de Dependencia Dixon-Coles ($\rho$):** Corrige el defecto clásico de los modelos de Poisson independientes, los cuales subestiman la probabilidad matemática de los empates con pocos goles (0-0 y 1-1) en el fútbol real.
    * **Simulación Monte Carlo ($N=200,000$):** Al generar 200,000 iteraciones estocásticas basadas en la distribución de probabilidad conjunta, el modelo converge con precisión infinitesimal en los mercados de goles e indicadores de victoria.
    """)

# 2. INTERFAZ DE SELECCIÓN DE EQUIPOS
col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    home_team = st.selectbox("Equipo Local (Fila)", sorted(list(todos_los_equipos.keys())), index=2) 
with col_sel2:
    away_team = st.selectbox("Equipo Visitante (Columna)", sorted(list(todos_los_equipos.keys())), index=7) 

# 3. PANEL LATERAL: CALIBRACIÓN EN VIVO (SLIDERS)
st.sidebar.header("🛠️ Panel de Calibración")
st.sidebar.markdown("Ajustá las fuerzas según alineaciones, lesiones o contexto del partido.")

st.sidebar.subheader(f"Fuerzas de {home_team}")
atk_home = st.sidebar.slider(f"Ataque {home_team}", 0.5, 3.5, float(todos_los_equipos[home_team]["atk"]), 0.05)
def_home = st.sidebar.slider(f"Defensa {home_team}", 0.5, 2.5, float(todos_los_equipos[home_team]["def"]), 0.05)

st.sidebar.subheader(f"Fuerzas de {away_team}")
atk_away = st.sidebar.slider(f"Ataque {away_team}", 0.5, 3.5, float(todos_los_equipos[away_team]["atk"]), 0.05)
def_away = st.sidebar.slider(f"Defensa {away_team}", 0.5, 2.5, float(todos_los_equipos[away_team]["def"]), 0.05)

st.sidebar.subheader("Ajuste de Escenario")
rho = st.sidebar.slider("Parámetro Dixon-Coles (rho)", -0.10, -0.01, -0.06, 0.01)

# BOTÓN DE SIMULACIÓN
if st.button("Generar Predicción Avanzada", type="primary"):
    
    lam_home = atk_home * def_away
    lam_away = atk_away * def_home
    max_g = 5
    N = 200000 
    
    def dc(i, j, l, m, r):
        if i == 0 and j == 0: return 1 - l * m * r
        if i == 0 and j == 1: return 1 + l * r
        if i == 1 and j == 0: return 1 + m * r
        if i == 1 and j == 1: return 1 - r
        return 1.0

    P = np.zeros((max_g + 1, max_g + 1))
    for i in range(max_g + 1):
        for j in range(max_g + 1):
            P[i, j] = poisson.pmf(i, lam_home) * poisson.pmf(j, lam_away) * dc(i, j, lam_home, lam_away, rho)
    P /= P.sum()

    # Simulación Monte Carlo
    flat = P.flatten()
    idx = np.random.choice(len(flat), size=N, p=flat)
    hg = idx // (max_g + 1)
    ag = idx % (max_g + 1)

    win_h = np.mean(hg > ag) * 100
    draw = np.mean(hg == ag) * 100
    win_a = np.mean(hg < ag) * 100
    btts = np.mean((hg > 0) & (ag > 0)) * 100
    
    total_goles = hg + ag
    o15 = np.mean(total_goles > 1.5) * 100
    o25 = np.mean(total_goles > 2.5) * 100
    o35 = np.mean(total_goles > 3.5) * 100

    # --- PRESENTACIÓN VISUAL EN LA WEB ---
    st.markdown("---")
    st.markdown(f"### 📊 Goles Esperados para este partido (xG): **{home_team} {lam_home:.2f}** vs **{lam_away:.2f} {away_team}**")
    
    c1, c2, c3 = st.columns(3)
    c1.metric(label=f"Victoria 🏠 {home_team}", value=f"{win_h:.1f}%")
    c2.metric(label="Empate 🤝", value=f"{draw:.1f}%")
    c3.metric(label=f"Victoria 🚀 {away_team}", value=f"{win_a:.1f}%")
    
    st.markdown("### 📈 Mercados de Goles Estadísticos")
    mg1, mg2, mg3, mg4 = st.columns(4)
    mg1.metric("Ambos Marcan (BTTS)", f"{btts:.1f}%")
    mg2.metric("Over 1.5 Goles", f"{o15:.1f}%")
    mg3.metric("Over 2.5 Goles", f"{o25:.1f}%")
    mg4.metric("Over 3.5 Goles", f"{o35:.1f}%")

    # Columnas combinadas para Gráfico + Matriz
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.markdown("### 🟥 Matriz de Probabilidad de Resultado Exacto (%)")
        st.info(f"⬇️ Filas: Goles de **{home_team}** | ➡️ Columnas: Goles de **{away_team}**")
        
        df_matriz = pd.DataFrame(
            P * 100, 
            columns=[f"{j} Gol(es) de {away_team}" for j in range(max_g + 1)],
            index=[f"{i} Gol(es) de {home_team}" for i in range(max_g + 1)]
        )
        st.dataframe(df_matriz.style.format("{:.2f}%").background_gradient(cmap="Reds"), use_container_width=True)

    with col_der:
        # --- MEJORA 2: GRÁFICO INTERACTIVO DE DISTRIBUCIÓN DE GOLES TOTALES ---
        st.markdown("### 📊 Distribución de Probabilidad de Goles Totales")
        st.caption("Frecuencia relativa observada a lo largo de las 200,000 simulaciones estocásticas.")
        
        goles_dist = pd.Series(total_goles).value_counts(normalize=True).sort_index() * 100
        df_grafico = pd.DataFrame({
            "Probabilidad (%)": goles_dist.values
        }, index=[f"{int(x)} Goles" for x in goles_dist.index])
        
        st.bar_chart(df_grafico)

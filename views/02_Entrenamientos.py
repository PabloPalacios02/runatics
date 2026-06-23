from datetime import date, timedelta

import plotly.express as px
import streamlit as st

from ui.app_state import get_datos

from ui.theme import aplicar_estilos, hero

from ui.charts import (
    grafica_tiempo_por_deporte,
    grafica_distancia_actividades,
)


def render():
    aplicar_estilos()

    df, salud = get_datos()

    hero(
        "Entrenamientos",
        "Analiza tus sesiones de Garmin y Strava por deporte, origen y periodo.",
    )

    df = df.copy()
    df["fecha"] = df["fecha"].dt.tz_localize(None)

    st.subheader("Filtros")

    c1, c2, c3 = st.columns(3)

    with c1:
        deporte = st.selectbox(
            "Deporte",
            ["Todos"] + sorted(df["deporte"].dropna().unique()),
        )

    with c2:
        origen = st.selectbox(
            "Origen",
            ["Todos"] + sorted(df["origen"].dropna().unique()),
        )

    with c3:
        dias = st.selectbox(
            "Periodo",
            ["7 días", "30 días", "90 días", "Todo"],
            index=2,
        )

    df_filtrado = df.copy()

    if deporte != "Todos":
        df_filtrado = df_filtrado[df_filtrado["deporte"] == deporte]

    if origen != "Todos":
        df_filtrado = df_filtrado[df_filtrado["origen"] == origen]

    if dias != "Todo":
        n = int(dias.split()[0])
        limite = date.today() - timedelta(days=n)
        df_filtrado = df_filtrado[df_filtrado["fecha"].dt.date >= limite]

    st.subheader("Resumen")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Sesiones", len(df_filtrado))
    c2.metric("Distancia", f"{round(df_filtrado['distancia_km'].sum(), 1)} km")
    c3.metric("Horas", f"{round(df_filtrado['duracion_min'].sum() / 60, 1)} h")

    if len(df_filtrado) > 0:
        c4.metric(
            "Duración media", f"{round(df_filtrado['duracion_min'].mean(), 1)} min"
        )
    else:
        c4.metric("Duración media", "-")

    if df_filtrado.empty:
        st.info("No hay actividades con esos filtros.")
        return

    st.subheader("Gráficas")

    col1, col2 = st.columns(2)

    with col1:
        grafica_tiempo_por_deporte(df_filtrado)

    with col2:
        grafica_distancia_actividades(df_filtrado)

    st.subheader("Tabla de actividades")

    columnas = [
        "fecha",
        "nombre",
        "deporte",
        "distancia_km",
        "duracion_min",
        "ritmo_min_km",
        "velocidad_kmh",
        "fc_media",
        "fc_max",
        "calorias",
        "origen",
    ]

    columnas_existentes = [c for c in columnas if c in df_filtrado.columns]

    st.dataframe(
        df_filtrado[columnas_existentes],
        use_container_width=True,
        hide_index=True,
    )

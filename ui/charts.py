import plotly.express as px
import streamlit as st


def grafica_peso(df):
    if df.empty:
        st.info("No hay datos de peso.")
        return

    fig = px.line(
        df,
        x="fecha",
        y="peso",
        markers=True,
        title="Histórico de peso",
    )

    fig.update_layout(
        height=400,
        xaxis_title="Fecha",
        yaxis_title="Peso (kg)",
    )

    st.plotly_chart(fig, use_container_width=True)


def grafica_sueno(df):
    if "sleep_hours" not in df.columns or not df["sleep_hours"].notna().any():
        st.info("No hay datos de sueño.")
        return

    fig = px.line(
        df,
        x="fecha",
        y="sleep_hours",
        markers=True,
        title="Horas de sueño",
    )

    fig.update_layout(height=400)

    st.plotly_chart(fig, use_container_width=True)


def grafica_fc_reposo(df):
    if "resting_hr" not in df.columns or not df["resting_hr"].notna().any():
        st.info("No hay datos de FC reposo.")
        return

    fig = px.line(
        df,
        x="fecha",
        y="resting_hr",
        markers=True,
        title="Frecuencia cardíaca en reposo",
    )

    fig.update_layout(height=400)

    st.plotly_chart(fig, use_container_width=True)


def grafica_estres(df):
    if "stress" not in df.columns or not df["stress"].notna().any():
        st.info("No hay datos de estrés.")
        return

    fig = px.line(
        df,
        x="fecha",
        y="stress",
        markers=True,
        title="Estrés Garmin",
    )

    fig.update_layout(height=400)

    st.plotly_chart(fig, use_container_width=True)


def grafica_consumo_vs_objetivo(progreso):
    fig = px.bar(
        progreso,
        x="Macro",
        y=["Consumido", "Objetivo"],
        barmode="group",
        title="Consumo vs objetivo",
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)


def grafica_tiempo_por_deporte(df):
    resumen = (
        df.groupby("deporte", as_index=False)["duracion_min"]
        .sum()
        .sort_values("duracion_min", ascending=False)
    )

    fig = px.bar(
        resumen,
        x="deporte",
        y="duracion_min",
        color="deporte",
        title="Tiempo por deporte",
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)


def grafica_distancia_actividades(df):
    fig = px.line(
        df.sort_values("fecha"),
        x="fecha",
        y="distancia_km",
        color="deporte",
        markers=True,
        title="Distancia por actividad",
    )

    fig.update_layout(height=450)

    st.plotly_chart(fig, use_container_width=True)

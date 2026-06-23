import plotly.express as px
import streamlit as st

from ui.app_state import get_datos
from core.training_metrics import calcular_recovery_score


def render():
    df, salud = get_datos()

    st.title("❤️ Recuperación")

    score, estado = calcular_recovery_score(salud, df)

    c1, c2 = st.columns(2)
    c1.metric("Recovery Score", f"{score}/100")
    c2.metric("Estado", estado)

    st.subheader("Datos Garmin")
    st.dataframe(salud, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if "sleep_hours" in salud.columns and salud["sleep_hours"].notna().any():
            fig = px.line(
                salud,
                x="fecha",
                y="sleep_hours",
                markers=True,
                title="Sueño",
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if "resting_hr" in salud.columns and salud["resting_hr"].notna().any():
            fig = px.line(
                salud,
                x="fecha",
                y="resting_hr",
                markers=True,
                title="FC reposo",
            )
            st.plotly_chart(fig, use_container_width=True)

    if "stress" in salud.columns and salud["stress"].notna().any():
        fig = px.line(
            salud,
            x="fecha",
            y="stress",
            markers=True,
            title="Estrés",
        )
        st.plotly_chart(fig, use_container_width=True)

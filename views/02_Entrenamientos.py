import streamlit as st
from ui.app_state import get_datos


def render():
    df, salud = get_datos()

    st.title("🏃 Entrenamientos")

    deporte = st.selectbox(
        "Filtrar deporte",
        ["Todos"] + sorted(df["deporte"].dropna().unique()),
    )

    if deporte != "Todos":
        df = df[df["deporte"] == deporte]

    st.dataframe(df, use_container_width=True)

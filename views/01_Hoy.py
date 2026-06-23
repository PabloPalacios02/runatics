from datetime import date
import streamlit as st

from ui.app_state import get_datos
from data_store.storage import cargar_perfil


def render():
    df, salud = get_datos()
    perfil = cargar_perfil()

    st.title("🏠 Hoy")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Peso", f"{perfil['peso']} kg")
    c2.metric("Edad", perfil["edad"])
    c3.metric("Actividades", len(df))
    c4.metric("Fecha", date.today().strftime("%d/%m/%Y"))

    st.subheader("Últimas actividades")
    st.dataframe(df.tail(10), use_container_width=True)

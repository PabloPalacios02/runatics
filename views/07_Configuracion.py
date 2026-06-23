import streamlit as st

from data_store.storage import cargar_perfil, guardar_perfil


def render():
    perfil = cargar_perfil()

    st.title("⚙️ Configuración")

    st.subheader("Perfil deportivo")

    with st.form("config_perfil"):
        peso = st.number_input(
            "Peso actual (kg)", value=float(perfil["peso"]), step=0.1
        )
        altura = st.number_input("Altura (cm)", value=float(perfil["altura"]), step=1.0)
        edad = st.number_input("Edad", value=int(perfil["edad"]), step=1)

        superavit = st.number_input(
            "Superávit para ganar masa muscular",
            value=int(perfil["superavit"]),
            step=50,
        )

        st.markdown("### Objetivos triatlón")

        swim = st.number_input(
            "Objetivo natación 1500 m",
            value=float(perfil["target_swim_min"]),
            step=1.0,
        )

        bike = st.number_input(
            "Objetivo bici 40 km",
            value=float(perfil["target_bike_min"]),
            step=1.0,
        )

        run = st.number_input(
            "Objetivo carrera 10 km",
            value=float(perfil["target_run_min"]),
            step=1.0,
        )

        if st.form_submit_button("Guardar configuración"):
            guardar_perfil(peso, altura, edad, superavit, swim, bike, run)
            st.success("Configuración guardada.")

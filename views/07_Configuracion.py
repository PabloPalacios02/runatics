import streamlit as st

from ui.theme import aplicar_estilos, hero
from ui.cards import metric_card
from data_store.storage import cargar_perfil, guardar_perfil


def render():
    aplicar_estilos()

    perfil = cargar_perfil()

    hero("Configuración", "Personaliza tus objetivos deportivos y nutricionales.")

    st.subheader("Perfil del usuario")

    with st.form("config_perfil_usuario"):
        c1, c2, c3 = st.columns(3)

        with c1:
            peso = st.number_input(
                "Peso actual (kg)",
                value=float(perfil["peso"]),
                step=0.1,
            )

        with c2:
            altura = st.number_input(
                "Altura (cm)",
                value=float(perfil["altura"]),
                step=1.0,
            )

        with c3:
            edad = st.number_input(
                "Edad",
                value=int(perfil["edad"]),
                step=1,
            )

        st.divider()

        st.subheader("Objetivo nutricional")

        superavit = st.number_input(
            "Superávit para ganar masa muscular (kcal)",
            value=int(perfil["superavit"]),
            step=50,
        )

        st.caption(
            "Un superávit moderado ayuda a ganar masa sin subir demasiada grasa."
        )

        st.divider()

        st.subheader("Objetivos de triatlón olímpico")

        c1, c2, c3 = st.columns(3)

        with c1:
            swim = st.number_input(
                "Natación 1500 m (min)",
                value=float(perfil["target_swim_min"]),
                step=1.0,
            )

        with c2:
            bike = st.number_input(
                "Bici 40 km (min)",
                value=float(perfil["target_bike_min"]),
                step=1.0,
            )

        with c3:
            run = st.number_input(
                "Carrera 10 km (min)",
                value=float(perfil["target_run_min"]),
                step=1.0,
            )

        guardar = st.form_submit_button("Guardar configuración")

        if guardar:
            guardar_perfil(
                peso,
                altura,
                edad,
                superavit,
                swim,
                bike,
                run,
            )
            st.success("Configuración guardada correctamente.")

    st.divider()

    st.subheader("Resumen actual")

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "Peso", f"{perfil['peso']} kg")
    metric_card(c2, "Altura", f"{perfil['altura']} cm")
    metric_card(c3, "Edad", perfil["edad"])
    metric_card(c4, "Superávit", f"{perfil['superavit']} kcal")

    c1, c2, c3 = st.columns(3)

    metric_card(c1, "🏊 Natación", f"{perfil['target_swim_min']} min")
    metric_card(c2, "🚴 Bici", f"{perfil['target_bike_min']} min")
    metric_card(c3, "🏃 Carrera", f"{perfil['target_run_min']} min")

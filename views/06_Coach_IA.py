import streamlit as st

from ui.app_state import get_datos
from data_store.storage import cargar_perfil
from core.ai_coach import preguntar_coach_ia


def render():
    df, salud = get_datos()
    perfil = cargar_perfil()

    st.title("🤖 Coach IA")

    pregunta = st.text_area(
        "Pregunta al entrenador",
        placeholder="Ejemplo: ¿Qué debería entrenar mañana?",
    )

    if st.button("Preguntar al coach"):
        if not pregunta.strip():
            st.warning("Escribe una pregunta.")
            return

        with st.spinner("Analizando tus datos..."):
            try:
                respuesta = preguntar_coach_ia(pregunta, df, salud, perfil)
                st.markdown(respuesta)
            except Exception as e:
                st.error(f"Error: {e}")

import streamlit as st


def render():
    st.title("🛠️ Ajustes")

    st.info("Aquí iremos añadiendo opciones generales de la app.")

    st.subheader("Estado actual")

    st.write("Datos de sesión:")

    estado = {
        "garmin_user_id": st.session_state.get("garmin_user_id"),
        "df cargado": "df" in st.session_state,
        "salud cargada": "salud" in st.session_state,
    }

    st.json(estado)

    if st.button("Borrar sesión local"):
        st.session_state.clear()
        st.rerun()

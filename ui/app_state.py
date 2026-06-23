from datetime import date, timedelta
import streamlit as st

from services.garmin_service import (
    login_garmin,
    cargar_garmin_actividades,
    obtener_salud_garmin,
)

from services.strava_service import cargar_strava
from core.activity_merge import fusionar_actividades

from data_store.storage import (
    configurar_directorio_usuario,
    set_user_data_dir,
)


def cargar_sidebar():
    set_user_data_dir(st.session_state.get("garmin_user_id", "default"))

    st.sidebar.title("🏊 RUNATICS")

    if usuario_logueado():
        st.sidebar.success(
            f"Usuario activo: {st.session_state.get('garmin_user_id', 'default')}"
        )

        pagina = st.sidebar.radio(
            "Navegación",
            [
                "Hoy",
                "Entrenamientos",
                "Planificación",
                "Nutrición",
                "Recuperación",
                "Coach IA",
                "Configuración",
                "Ajustes",
            ],
        )

        if st.sidebar.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

        return pagina

    st.sidebar.header("🔐 Iniciar sesión Garmin")

    email = st.sidebar.text_input("Email Garmin")
    password = st.sidebar.text_input("Contraseña Garmin", type="password")

    hoy = date.today()

    rango = st.sidebar.date_input(
        "Periodo",
        (
            hoy - timedelta(days=90),
            hoy,
        ),
    )

    if st.sidebar.button("Sincronizar datos"):
        if not email or not password:
            st.sidebar.error("Introduce email y contraseña")
            return None

        try:
            inicio, fin = rango

            with st.spinner("Sincronizando..."):
                client = login_garmin(email, password)
                perfil = client.get_user_profile()
                user_id = perfil.get("id", "default")

                st.session_state["perfil_garmin"] = perfil
                st.session_state["garmin_user_id"] = user_id

                configurar_directorio_usuario(user_id)

                df_garmin = cargar_garmin_actividades(client, inicio, fin)
                salud = obtener_salud_garmin(client, dias=21)
                df_strava = cargar_strava(inicio, fin)

                df_total = fusionar_actividades(df_garmin, df_strava)

                st.session_state["df"] = df_total
                st.session_state["salud"] = salud
                st.session_state["df_garmin"] = df_garmin
                st.session_state["df_strava"] = df_strava

            st.sidebar.success("Datos sincronizados")
            st.rerun()

        except Exception as e:
            st.sidebar.error(str(e))

    return None


def get_datos():

    if "df" not in st.session_state:
        st.warning("Sincroniza primero Garmin y Strava.")
        st.stop()

    return (
        st.session_state["df"],
        st.session_state["salud"],
    )


def usuario_logueado():
    return "df" in st.session_state and "salud" in st.session_state

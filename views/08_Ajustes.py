import streamlit as st

from ui.theme import aplicar_estilos, hero
from ui.cards import metric_card
from services.supabase_service import get_supabase_client


def comprobar_supabase():
    try:
        supabase = get_supabase_client()
        res = supabase.table("profiles").select("*").limit(1).execute()
        return True, res.data
    except Exception as e:
        return False, str(e)


def render():
    aplicar_estilos()

    hero("Ajustes", "Estado interno de la aplicación y herramientas de mantenimiento.")

    st.subheader("Estado de la sesión")

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "Usuario", st.session_state.get("garmin_user_id", "-"))
    metric_card(c2, "Actividades", "Sí" if "df" in st.session_state else "No")
    metric_card(c3, "Salud", "Sí" if "salud" in st.session_state else "No")
    metric_card(
        c4, "Perfil Garmin", "Sí" if "perfil_garmin" in st.session_state else "No"
    )

    with st.expander("Ver estado completo"):
        st.json(
            {
                "garmin_user_id": st.session_state.get("garmin_user_id"),
                "actividades cargadas": "df" in st.session_state,
                "salud cargada": "salud" in st.session_state,
                "perfil Garmin cargado": "perfil_garmin" in st.session_state,
            }
        )

    st.divider()

    st.subheader("Conexión Supabase")

    if st.button("Comprobar conexión Supabase"):
        ok, resultado = comprobar_supabase()

        if ok:
            st.success("Supabase conectado correctamente.")
            st.write(resultado)
        else:
            st.error("Error conectando con Supabase.")
            st.code(resultado)

    st.divider()

    st.subheader("Acciones")

    if st.button("Borrar sesión local"):
        st.session_state.clear()
        st.rerun()

    st.caption(
        "Esto no borra datos de Supabase. Solo cierra la sesión cargada en esta visita."
    )

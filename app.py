import importlib.util
from pathlib import Path
import streamlit as st

from config.settings import APP_TITLE, APP_CAPTION
from ui.app_state import cargar_sidebar

st.set_page_config(
    page_title="RUNATICS",
    page_icon="🏊",
    layout="wide",
)

st.title(APP_TITLE)
st.caption(APP_CAPTION)

pagina = cargar_sidebar()


VIEWS = {
    "Hoy": "views/01_Hoy.py",
    "Entrenamientos": "views/02_Entrenamientos.py",
    "Planificación": "views/03_Planificacion.py",
    "Nutrición": "views/04_Nutricion.py",
    "Recuperación": "views/05_Recuperacion.py",
    "Coach IA": "views/06_Coach_IA.py",
    "Configuración": "views/07_Configuracion.py",
    "Ajustes": "views/08_Ajustes.py",
}


def cargar_vista(path):
    path = Path(path)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.render()


if pagina is None:
    st.markdown("## Inicia sesión para acceder a RUNATICS")
    st.info(
        "Introduce tus credenciales de Garmin en la barra lateral y sincroniza tus datos."
    )
else:
    cargar_vista(VIEWS[pagina])

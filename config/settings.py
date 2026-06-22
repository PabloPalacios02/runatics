from datetime import date
import tomli as tomllib
import streamlit as st

APP_TITLE = "🏊🚴🏃 RUNATICS"
APP_CAPTION = "Garmin = salud/recuperación | Strava = actividades deportivas"
OBJETIVO_FECHA = date(2026, 9, 27)
BASE_DATA_DIR = "data"


def cargar_secrets() -> dict:
    try:
        return dict(st.secrets)
    except Exception:
        with open("secrets.toml", "rb") as f:
            return tomllib.load(f)

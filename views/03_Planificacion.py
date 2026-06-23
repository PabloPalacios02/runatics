import pandas as pd
import streamlit as st

from ui.app_state import get_datos
from data_store.storage import cargar_perfil
from core.training_metrics import (
    generar_entrenamiento_detallado,
    analizar_cumplimiento_entrenos,
    predictor_inteligente,
    replanificar_semana_real,
    calcular_recovery_score,
)


def render():
    df, salud = get_datos()
    perfil = cargar_perfil()

    st.title("📅 Planificación")

    plan, pred_base, fase, recuperacion_baja = generar_entrenamiento_detallado(
        df, salud, perfil
    )

    cumplimiento = analizar_cumplimiento_entrenos(df)
    pred, gaps, tendencias = predictor_inteligente(df, salud, perfil)
    plan = replanificar_semana_real(plan, cumplimiento, gaps, recuperacion_baja)
    recovery_score, recovery_estado = calcular_recovery_score(salud, df)

    st.write(f"Fase actual: **{fase}**")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏊 1500 m", f"{pred['swim_1500_min']} min")
    c2.metric("🚴 40 km", f"{pred['bike_40k_min']} min")
    c3.metric("🏃 10 km", f"{pred['run_10k_min']} min")
    c4.metric("❤️ Recovery", f"{recovery_score}/100")

    st.write(f"Estado recuperación: **{recovery_estado}**")

    if recuperacion_baja:
        st.warning("Plan suavizado por recuperación baja.")
    else:
        st.success("Planificación normal.")

    st.subheader("🎯 Objetivo vs predicción")
    st.dataframe(gaps, use_container_width=True)

    st.subheader("📊 Tendencias")
    st.dataframe(tendencias, use_container_width=True)

    st.subheader("📈 Cumplimiento últimos 7 días")
    st.dataframe(cumplimiento, use_container_width=True)

    st.subheader("📋 Semana propuesta")
    st.dataframe(plan, use_container_width=True)

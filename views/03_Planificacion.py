import streamlit as st

from ui.theme import aplicar_estilos, hero

from ui.app_state import get_datos
from data_store.storage import cargar_perfil
from core.training_metrics import (
    generar_entrenamiento_detallado,
    analizar_cumplimiento_entrenos,
    predictor_inteligente,
    replanificar_semana_real,
    calcular_recovery_score,
)

from datetime import timedelta
from ui.cards import metric_card

from data_store.storage import (
    cargar_perfil,
    cargar_competicion_principal,
    cargar_competiciones_secundarias_activas,
)
from core.competition_logic import (
    dias_hasta,
    fase_por_competicion,
    resumen_competicion,
    enfoque_planificacion,
    adaptar_plan_a_competiciones,
)


def render():

    aplicar_estilos()

    df, salud = get_datos()
    perfil = cargar_perfil()

    comp_principal = cargar_competicion_principal()
    secundarias = cargar_competiciones_secundarias_activas()

    fase_adaptada = fase_por_competicion(comp_principal)
    dias_objetivo = dias_hasta(comp_principal)
    enfoque = enfoque_planificacion(comp_principal, secundarias)

    hero(
        "Planificación",
        "Plan semanal adaptado según tu recuperación, carga y objetivos.",
    )

    plan, pred_base, fase, recuperacion_baja = generar_entrenamiento_detallado(
        df, salud, perfil
    )

    cumplimiento = analizar_cumplimiento_entrenos(df)
    pred, gaps, tendencias = predictor_inteligente(df, salud, perfil)
    plan = replanificar_semana_real(plan, cumplimiento, gaps, recuperacion_baja)
    plan = adaptar_plan_a_competiciones(
        plan,
        comp_principal,
        secundarias,
        recuperacion_baja,
    )
    plan["Contexto competición"] = enfoque
    recovery_score, recovery_estado = calcular_recovery_score(salud, df)
    fecha_max = df["fecha"].dt.date.max()
    ult7 = df[df["fecha"].dt.date >= fecha_max - timedelta(days=7)]

    st.subheader("Estado general")

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "Fase", fase_adaptada)
    metric_card(c2, "Recovery", f"{recovery_score}/100")
    metric_card(c3, "Estado", recovery_estado)
    metric_card(c4, "Sesiones semana", len(ult7))
    st.subheader("Objetivo de planificación")

    if comp_principal is not None:
        st.success(f"Principal: {resumen_competicion(comp_principal)}")
        st.write(f"Quedan **{dias_objetivo} días**.")
    else:
        st.info("Sin competición principal. Plan general equilibrado.")

    st.info(enfoque)

    if not secundarias.empty:
        with st.expander("Competiciones secundarias que afectan al plan"):
            st.dataframe(
                secundarias[
                    [
                        "nombre",
                        "fecha",
                        "tipo",
                        "distancia",
                        "distancia_km",
                        "prioridad",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    if recuperacion_baja:
        st.warning("Recuperación baja: la semana se ha suavizado automáticamente.")
    else:
        st.success("Recuperación correcta: planificación normal.")

    st.divider()

    st.subheader("Predicción objetivo")

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "🏊 1500 m", f"{pred['swim_1500_min']} min")
    metric_card(c2, "🚴 40 km", f"{pred['bike_40k_min']} min")
    metric_card(c3, "🏃 10 km", f"{pred['run_10k_min']} min")
    metric_card(c4, "⏱️ Total", f"{pred['total_estimado_min']} min")

    with st.expander("Ver objetivo vs predicción"):
        st.dataframe(gaps, use_container_width=True, hide_index=True)

    with st.expander("Ver tendencias últimos 90 días"):
        st.dataframe(tendencias, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Cumplimiento semanal")

    st.dataframe(
        cumplimiento,
        use_container_width=True,
        hide_index=True,
    )

    bajos = cumplimiento[cumplimiento["Estado"] == "Bajo"]["Disciplina"].tolist()
    excesos = cumplimiento[cumplimiento["Estado"] == "Exceso"]["Disciplina"].tolist()

    if bajos:
        st.warning("Falta trabajo en: " + ", ".join(bajos))

    if excesos:
        st.info("Carga alta en: " + ", ".join(excesos))

    if not bajos and not excesos:
        st.success("La distribución semanal está bastante equilibrada.")

    st.divider()

    st.subheader("Semana propuesta")

    for _, fila in plan.iterrows():
        with st.container(border=True):
            c1, c2 = st.columns([1, 3])

            with c1:
                st.markdown(f"### {fila['Día']}")
                st.write(f"**{fila['Sesión']}**")
                st.caption(f"Intensidad: {fila['Intensidad']}")

            with c2:
                st.write(fila["Entrenamiento detallado"])
                st.caption(f"Objetivo: {fila['Objetivo']}")

                if "Ajuste automático" in fila and fila["Ajuste automático"]:
                    st.info(fila["Ajuste automático"])

                if "Adaptación competición" in fila and fila["Adaptación competición"]:
                    st.success(fila["Adaptación competición"])

from datetime import date, timedelta
import streamlit as st

from ui.cards import metric_card
from ui.theme import aplicar_estilos, hero
from ui.app_state import get_datos

from data_store.storage import (
    cargar_perfil,
    cargar_diario,
    cargar_competicion_principal,
    cargar_competiciones_secundarias_activas,
    cargar_competiciones_activas,
)

from core.training_metrics import (
    calcular_objetivos_dinamicos,
    generar_entrenamiento_detallado,
    calcular_recovery_score,
)

from core.competition_logic import (
    dias_hasta,
    fase_por_competicion,
    resumen_competicion,
)

from core.competition_metrics import predicciones_para_competicion


def render():
    aplicar_estilos()

    df, salud = get_datos()
    perfil = cargar_perfil()

    comp_principal = cargar_competicion_principal()
    secundarias = cargar_competiciones_secundarias_activas()
    fase_competicion = fase_por_competicion(comp_principal)
    dias_competicion = dias_hasta(comp_principal)

    hero("Hoy", "Resumen rápido de entrenamiento, nutrición y recuperación.")

    hoy = date.today()

    objetivos_hoy = calcular_objetivos_dinamicos(
        perfil["peso"],
        perfil["altura"],
        perfil["edad"],
        salud,
        df,
        hoy,
        perfil["superavit"],
    )

    plan, pred, fase, recuperacion_baja = generar_entrenamiento_detallado(
        df, salud, perfil
    )

    recovery_score, recovery_estado = calcular_recovery_score(salud, df)

    ult7 = df[df["fecha"].dt.date >= hoy - timedelta(days=7)]

    km_run = round(ult7[ult7["deporte"] == "Running"]["distancia_km"].sum(), 1)
    km_bici = round(ult7[ult7["deporte"] == "Bici"]["distancia_km"].sum(), 1)
    km_nat = round(ult7[ult7["deporte"] == "Natación"]["distancia_km"].sum(), 2)
    sesiones_gym = len(ult7[ult7["deporte"] == "Gimnasio"])

    st.subheader("Resumen rápido")

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "🏃 Running 7 días", f"{km_run} km")
    metric_card(c2, "🚴 Bici 7 días", f"{km_bici} km")
    metric_card(c3, "🏊 Natación 7 días", f"{km_nat} km")
    metric_card(c4, "🏋️ Gimnasio", sesiones_gym)

    st.subheader("Estado de hoy")

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "❤️ Recovery", f"{recovery_score}/100")
    metric_card(c2, "Estado", recovery_estado)
    metric_card(c3, "Fase", fase_competicion)
    metric_card(
        c4, "Días objetivo", "-" if dias_competicion is None else dias_competicion
    )

    st.subheader("Objetivo deportivo")

    if comp_principal is not None:
        st.success(f"Principal: {resumen_competicion(comp_principal)}")

        if not secundarias.empty:
            with st.expander("Competiciones secundarias activas"):
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
    else:
        st.info(
            "No hay competición principal activa. La app usará una planificación general."
        )

    competiciones_activas = cargar_competiciones_activas()

    if competiciones_activas is not None and not competiciones_activas.empty:
        st.subheader("Predicciones por competición")

        for _, comp in competiciones_activas.iterrows():
            df_pred = predicciones_para_competicion(
                df,
                comp,
                pred_triatlon=pred,
            )

            with st.container(border=True):
                st.markdown(f"### {comp['nombre']}")
                st.write(
                    f"Tipo: **{comp['tipo']}** | Distancia: **{comp['distancia_km']:g} km**"
                )

                if df_pred.empty:
                    st.info("No hay predicción específica para esta competición.")
                else:
                    st.dataframe(df_pred, use_container_width=True, hide_index=True)

    if recuperacion_baja:
        st.warning("Recuperación baja: hoy conviene reducir intensidad.")
    else:
        st.success("Recuperación correcta: puedes entrenar normal.")

    st.subheader("Macros objetivo")

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "🔥 Kcal", objetivos_hoy["calorias"])
    metric_card(c2, "🥩 Proteína", f"{objetivos_hoy['proteina']} g")
    metric_card(c3, "🍚 Carbos", f"{objetivos_hoy['carbos']} g")
    metric_card(c4, "🥑 Grasas", f"{objetivos_hoy['grasas']} g")

    diario = cargar_diario()
    diario_hoy = diario[diario["fecha"] == hoy]

    if not diario_hoy.empty:
        kcal = round(diario_hoy["kcal"].sum())
        proteina = round(diario_hoy["proteina"].sum())
        carbos = round(diario_hoy["carbos"].sum())
        grasas = round(diario_hoy["grasas"].sum())

        st.caption(
            f"Consumido hoy: {kcal} kcal | "
            f"{proteina} g proteína | "
            f"{carbos} g carbos | "
            f"{grasas} g grasas"
        )
    else:
        st.caption("Todavía no has registrado comidas hoy.")

    st.subheader("Entreno recomendado")

    st.dataframe(
        plan.head(1),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Últimas actividades")

    columnas = [
        "fecha",
        "nombre",
        "deporte",
        "distancia_km",
        "duracion_min",
        "ritmo_min_km",
        "velocidad_kmh",
        "origen",
    ]

    columnas_existentes = [c for c in columnas if c in df.columns]

    st.dataframe(
        df[columnas_existentes].head(10),
        use_container_width=True,
        hide_index=True,
    )

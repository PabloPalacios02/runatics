import streamlit as st

from ui.theme import aplicar_estilos, hero
from ui.app_state import get_datos
from ui.cards import metric_card
from ui.charts import grafica_sueno, grafica_fc_reposo, grafica_estres

from core.training_metrics import calcular_recovery_score


def valor_o_guion(valor, formato):
    if valor != valor:
        return "-"
    return formato.format(valor)


def render():
    aplicar_estilos()

    df, salud = get_datos()

    hero("Recuperación", "Analiza sueño, estrés, frecuencia cardíaca y estado general.")

    score, estado = calcular_recovery_score(salud, df)

    sleep_avg = salud["sleep_hours"].dropna().tail(7).mean()
    resting_avg = salud["resting_hr"].dropna().tail(7).mean()
    stress_avg = salud["stress"].dropna().tail(7).mean()

    st.subheader("Estado actual")

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "Recovery Score", f"{score}/100")
    metric_card(c2, "Estado", estado)
    metric_card(c3, "Sueño medio", valor_o_guion(sleep_avg, "{:.1f} h"))
    metric_card(c4, "FC reposo", valor_o_guion(resting_avg, "{:.0f} bpm"))

    if score >= 80:
        st.success("Buena recuperación. Puedes entrenar con normalidad.")
    elif score >= 60:
        st.warning("Recuperación aceptable. Evita acumular demasiada intensidad.")
    else:
        st.error("Recuperación baja. Prioriza descanso, sueño y baja intensidad.")

    st.divider()

    st.subheader("Indicadores Garmin")

    c1, c2, c3 = st.columns(3)

    metric_card(c1, "Sueño 7 días", valor_o_guion(sleep_avg, "{:.1f} h"))
    metric_card(c2, "Estrés 7 días", valor_o_guion(stress_avg, "{:.0f}"))
    metric_card(c3, "FC reposo 7 días", valor_o_guion(resting_avg, "{:.0f} bpm"))

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Sueño",
            "FC reposo",
            "Estrés",
            "Tabla",
        ]
    )

    with tab1:
        grafica_sueno(salud)

    with tab2:
        grafica_fc_reposo(salud)

    with tab3:
        grafica_estres(salud)

    with tab4:
        st.dataframe(
            salud,
            use_container_width=True,
            hide_index=True,
        )

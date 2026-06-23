import streamlit as st

from ui.theme import aplicar_estilos, hero

from ui.app_state import get_datos
from data_store.storage import cargar_perfil, cargar_diario, cargar_peso
from core.ai_coach import preguntar_coach_ia


def render():

    aplicar_estilos()

    df, salud = get_datos()
    perfil = cargar_perfil()

    hero("Coach IA", "Consulta a tu entrenador personal basado en tus datos reales.")

    st.subheader("Preguntas rápidas")

    c1, c2, c3 = st.columns(3)

    pregunta_rapida = None

    with c1:
        if st.button("¿Qué entreno mañana?"):
            pregunta_rapida = (
                "Analiza mis datos recientes y dime qué debería entrenar mañana."
            )

    with c2:
        if st.button("¿Estoy recuperado?"):
            pregunta_rapida = (
                "Analiza mi recuperación, sueño, estrés, FC reposo y carga reciente."
            )

    with c3:
        if st.button("¿Cómo voy para el triatlón?"):
            pregunta_rapida = "Analiza mi progreso para el triatlón olímpico y dime puntos fuertes y débiles."

    c4, c5, c6 = st.columns(3)

    with c4:
        if st.button("¿Estoy comiendo bien?"):
            pregunta_rapida = "Analiza mi nutrición, proteína, calorías y si estoy comiendo bien para ganar masa muscular y preparar triatlón."

    with c5:
        if st.button("Ajusta mi semana"):
            pregunta_rapida = (
                "Replanifica mi semana según mi carga, recuperación y objetivos."
            )

    with c6:
        if st.button("Riesgo de sobrecarga"):
            pregunta_rapida = "Analiza si tengo riesgo de sobrecarga o lesión según mis últimos entrenamientos."

    st.divider()

    pregunta_manual = st.text_area(
        "Pregunta personalizada",
        placeholder="Ejemplo: ¿Debería hacer series mañana o mejor rodaje suave?",
        height=120,
    )

    pregunta_final = pregunta_rapida or pregunta_manual

    if st.button("Preguntar al coach"):
        if not pregunta_final or not pregunta_final.strip():
            st.warning("Escribe una pregunta o usa una pregunta rápida.")
            return

        with st.spinner("Analizando tus datos..."):
            try:
                respuesta = preguntar_coach_ia(
                    pregunta_final,
                    df,
                    salud,
                    perfil,
                )

                st.markdown(respuesta)

            except Exception as e:
                st.error(f"Error consultando al coach IA: {e}")

    st.divider()

    with st.expander("Contexto usado por el coach"):
        st.write("Actividades recientes")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)

        st.write("Salud reciente")
        st.dataframe(salud.tail(10), use_container_width=True, hide_index=True)

        try:
            diario = cargar_diario()
            st.write("Nutrición registrada")
            st.dataframe(diario.tail(10), use_container_width=True, hide_index=True)
        except Exception:
            st.info("No hay datos de nutrición disponibles.")

        try:
            peso = cargar_peso()
            st.write("Peso registrado")
            st.dataframe(peso.tail(10), use_container_width=True, hide_index=True)
        except Exception:
            st.info("No hay datos de peso disponibles.")

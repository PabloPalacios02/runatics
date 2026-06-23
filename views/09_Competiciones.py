from datetime import date

import streamlit as st

from ui.theme import aplicar_estilos, hero
from ui.cards import metric_card
from data_store.storage import (
    cargar_competiciones,
    guardar_competicion,
    actualizar_competicion,
    eliminar_competicion,
    cargar_competicion_principal,
)

TIPOS = [
    "Triatlón",
    "Running",
    "Ciclismo",
    "Natación",
    "Gimnasio",
    "Otro",
]

DISTANCIAS = [
    "Sprint",
    "Olímpico",
    "Half Ironman",
    "Ironman",
    "5K",
    "10K",
    "Media Maratón",
    "Maratón",
    "Otra",
]

DISTANCIAS_PREDEFINIDAS = {
    "Sprint": 25.75,
    "Olímpico": 51.5,
    "Half Ironman": 113,
    "Ironman": 226,
    "5K": 5,
    "10K": 10,
    "Media Maratón": 21.1,
    "Maratón": 42.2,
}


def render():
    aplicar_estilos()

    hero(
        "Competiciones",
        "Gestiona tus objetivos deportivos y marca una competición principal.",
    )

    competicion_principal = cargar_competicion_principal()

    if competicion_principal is not None:
        dias = (competicion_principal["fecha"] - date.today()).days

        c1, c2, c3, c4 = st.columns(4)

        metric_card(c1, "Objetivo principal", competicion_principal["nombre"])
        metric_card(c2, "Tipo", competicion_principal["tipo"])
        metric_card(c3, "Días restantes", dias)
        metric_card(c4, "Prioridad", competicion_principal["prioridad"])
    else:
        st.info("Todavía no hay una competición principal activa.")

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        [
            "Nueva competición",
            "Listado",
            "Editar / borrar",
        ]
    )

    with tab1:
        crear_competicion()

    with tab2:
        listar_competiciones()

    with tab3:
        editar_competiciones()


def crear_competicion():
    st.subheader("Añadir competición")

    with st.form("form_nueva_competicion"):
        nombre = st.text_input(
            "Nombre",
            placeholder="Ej: Triatlón Olímpico Valencia, 10K Alcoy, Marcha ciclista...",
        )

        fecha = st.date_input("Fecha", value=date.today())

        tipo = st.selectbox("Tipo", TIPOS)

        distancia = st.selectbox("Distancia", DISTANCIAS)

        if distancia == "Otra":
            distancia_km = st.number_input(
                "Distancia exacta (km)",
                min_value=0.1,
                value=5.0,
                step=0.1,
            )
        else:
            distancia_km = DISTANCIAS_PREDEFINIDAS.get(distancia, 0)
            st.info(f"Distancia estimada: {distancia_km:g} km")

        objetivo_swim_min = 0
        objetivo_bike_min = 0
        objetivo_run_min = 0

        if tipo == "Triatlón":
            st.markdown("### Objetivos por disciplina")

            c1, c2, c3 = st.columns(3)

            with c1:
                objetivo_swim_min = st.number_input(
                    "Objetivo natación (min)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                )

            with c2:
                objetivo_bike_min = st.number_input(
                    "Objetivo bici (min)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                )

            with c3:
                objetivo_run_min = st.number_input(
                    "Objetivo carrera (min)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                )

        objetivo_tiempo_min = st.number_input(
            "Objetivo de tiempo total (min)",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

        prioridad = st.selectbox(
            "Prioridad",
            ["A", "B", "C"],
            help="A = importante, B = secundaria, C = baja prioridad",
        )

        es_principal = st.checkbox(
            "Marcar como competición principal",
            value=False,
            help="Solo debe haber una competición principal activa.",
        )

        notas = st.text_area(
            "Notas",
            placeholder="Objetivo, estrategia, circuito, sensaciones, material...",
        )

        activa = st.checkbox("Activa", value=True)

        guardar = st.form_submit_button("Guardar competición")

        if guardar:
            if not nombre.strip():
                st.error("Introduce un nombre.")
                return

            guardar_competicion(
                nombre=nombre,
                fecha=fecha,
                tipo=tipo,
                distancia=distancia,
                distancia_km=distancia_km,
                prioridad=prioridad,
                objetivo_tiempo_min=objetivo_tiempo_min,
                notas=notas,
                objetivo_swim_min=objetivo_swim_min,
                objetivo_bike_min=objetivo_bike_min,
                objetivo_run_min=objetivo_run_min,
                activa=activa,
                es_principal=es_principal,
            )

            st.success("Competición guardada.")
            st.rerun()


def listar_competiciones():
    st.subheader("Competiciones registradas")

    df = cargar_competiciones()

    if df.empty:
        st.info("No hay competiciones registradas.")
        return

    st.dataframe(
        df.drop(columns=["id"], errors="ignore"),
        use_container_width=True,
        hide_index=True,
    )


def editar_competiciones():
    st.subheader("Editar o borrar competición")

    df = cargar_competiciones()

    if df.empty:
        st.info("No hay competiciones para editar.")
        return

    opciones = {f"{row['nombre']} - {row['fecha']}": row for _, row in df.iterrows()}

    seleccion = st.selectbox(
        "Selecciona competición",
        list(opciones.keys()),
    )

    comp = opciones[seleccion]

    tipo_actual = comp["tipo"] if comp["tipo"] in TIPOS else "Otro"
    distancia_actual = comp["distancia"] if comp["distancia"] in DISTANCIAS else "Otra"
    prioridad_actual = (
        comp["prioridad"] if comp["prioridad"] in ["A", "B", "C"] else "A"
    )

    with st.form("form_editar_competicion"):
        nombre = st.text_input("Nombre", value=comp["nombre"])

        fecha = st.date_input("Fecha", value=comp["fecha"])

        tipo = st.selectbox(
            "Tipo",
            TIPOS,
            index=TIPOS.index(tipo_actual),
        )

        distancia = st.selectbox(
            "Distancia",
            DISTANCIAS,
            index=DISTANCIAS.index(distancia_actual),
        )

        if distancia == "Otra":
            distancia_km = st.number_input(
                "Distancia exacta (km)",
                min_value=0.1,
                value=float(comp["distancia_km"] or 5.0),
                step=0.1,
            )
        else:
            distancia_km = DISTANCIAS_PREDEFINIDAS.get(distancia, 0)
            st.info(f"Distancia estimada: {distancia_km:g} km")

        objetivo_swim_min = float(comp.get("objetivo_swim_min") or 0)
        objetivo_bike_min = float(comp.get("objetivo_bike_min") or 0)
        objetivo_run_min = float(comp.get("objetivo_run_min") or 0)

        if tipo == "Triatlón":
            st.markdown("### Objetivos por disciplina")

            c1, c2, c3 = st.columns(3)

            with c1:
                objetivo_swim_min = st.number_input(
                    "Objetivo natación (min)",
                    min_value=0.0,
                    value=objetivo_swim_min,
                    step=1.0,
                )

            with c2:
                objetivo_bike_min = st.number_input(
                    "Objetivo bici (min)",
                    min_value=0.0,
                    value=objetivo_bike_min,
                    step=1.0,
                )

            with c3:
                objetivo_run_min = st.number_input(
                    "Objetivo carrera (min)",
                    min_value=0.0,
                    value=objetivo_run_min,
                    step=1.0,
                )

        objetivo_tiempo_min = st.number_input(
            "Objetivo tiempo total (min)",
            min_value=0.0,
            value=float(comp["objetivo_tiempo_min"] or 0),
            step=1.0,
        )

        prioridad = st.selectbox(
            "Prioridad",
            ["A", "B", "C"],
            index=["A", "B", "C"].index(prioridad_actual),
        )

        es_principal = st.checkbox(
            "Marcar como competición principal",
            value=bool(comp["es_principal"]),
        )

        notas = st.text_area(
            "Notas",
            value=comp["notas"] or "",
        )

        activa = st.checkbox(
            "Activa",
            value=bool(comp["activa"]),
        )

        actualizar = st.form_submit_button("Actualizar competición")

        if actualizar:
            actualizar_competicion(
                competition_id=comp["id"],
                nombre=nombre,
                fecha=fecha,
                tipo=tipo,
                distancia=distancia,
                distancia_km=distancia_km,
                prioridad=prioridad,
                objetivo_tiempo_min=objetivo_tiempo_min,
                notas=notas,
                objetivo_swim_min=objetivo_swim_min,
                objetivo_bike_min=objetivo_bike_min,
                objetivo_run_min=objetivo_run_min,
                activa=activa,
                es_principal=es_principal,
            )

            st.success("Competición actualizada.")
            st.rerun()

    st.warning("Zona peligrosa")

    if st.button("Borrar competición"):
        eliminar_competicion(comp["id"])
        st.success("Competición eliminada.")
        st.rerun()

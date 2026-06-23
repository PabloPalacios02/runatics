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
            placeholder="Ej: Triatlón Olímpico Valencia",
        )

        fecha = st.date_input(
            "Fecha",
            value=date.today(),
        )

        tipo = st.selectbox(
            "Tipo",
            [
                "Triatlón",
                "Running",
                "Ciclismo",
                "Natación",
                "Gimnasio",
                "Otro",
            ],
        )

        distancia = st.selectbox(
            "Distancia",
            [
                "Sprint",
                "Olímpico",
                "Half Ironman",
                "Ironman",
                "5K",
                "10K",
                "Media Maratón",
                "Maratón",
                "Otra",
            ],
        )

        distancias_predefinidas = {
            "Sprint": 25.75,
            "Olímpico": 51.5,
            "Half Ironman": 113,
            "Ironman": 226,
            "5K": 5,
            "10K": 10,
            "Media Maratón": 21.1,
            "Maratón": 42.2,
        }

        if distancia == "Otra":
            distancia_km = st.number_input(
                "Distancia exacta (km)",
                min_value=0.0,
                value=0.0,
                step=0.1,
            )
        else:
            distancia_km = distancias_predefinidas.get(distancia, 0)
            st.info(f"Distancia estimada: {distancia_km} km")

        es_principal = st.checkbox(
            "Marcar como competición principal",
            value=False,
            help="Solo puede haber una competición principal activa.",
        )

        prioridad = st.selectbox(
            "Prioridad",
            ["A", "B", "C"],
            help="A = objetivo principal, B = importante, C = secundaria",
        )

        objetivo_tiempo_min = st.number_input(
            "Objetivo de tiempo total (min)",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

        notas = st.text_area(
            "Notas",
            placeholder="Objetivo, circuito, sensaciones, estrategia...",
        )

        activa = st.checkbox(
            "Activa",
            value=True,
        )

        guardar = st.form_submit_button("Guardar competición")

        if guardar:
            if not nombre.strip():
                st.error("Introduce un nombre.")
                return

            guardar_competicion(
                nombre,
                fecha,
                tipo,
                distancia,
                prioridad,
                objetivo_tiempo_min,
                notas,
                activa,
            )

            st.success("Competición guardada.")


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

    with st.form("form_editar_competicion"):
        nombre = st.text_input("Nombre", value=comp["nombre"])

        fecha = st.date_input("Fecha", value=comp["fecha"])

        tipo = st.selectbox(
            "Tipo",
            [
                "Triatlón",
                "Running",
                "Ciclismo",
                "Natación",
                "Gimnasio",
                "Otro",
            ],
            index=(
                [
                    "Triatlón",
                    "Running",
                    "Ciclismo",
                    "Natación",
                    "Gimnasio",
                    "Otro",
                ].index(comp["tipo"])
                if comp["tipo"]
                in [
                    "Triatlón",
                    "Running",
                    "Ciclismo",
                    "Natación",
                    "Gimnasio",
                    "Otro",
                ]
                else 0
            ),
        )

        distancia = st.selectbox(
            "Distancia",
            [
                "Sprint",
                "Olímpico",
                "Half Ironman",
                "Ironman",
                "5K",
                "10K",
                "Media Maratón",
                "Maratón",
                "Otra",
            ],
            index=(
                [
                    "Sprint",
                    "Olímpico",
                    "Half Ironman",
                    "Ironman",
                    "5K",
                    "10K",
                    "Media Maratón",
                    "Maratón",
                    "Otra",
                ].index(comp["distancia"])
                if comp["distancia"]
                in [
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
                else 0
            ),
        )

        prioridad = st.selectbox(
            "Prioridad",
            ["A", "B", "C"],
            index=(
                ["A", "B", "C"].index(comp["prioridad"])
                if comp["prioridad"] in ["A", "B", "C"]
                else 0
            ),
        )

        objetivo_tiempo_min = st.number_input(
            "Objetivo tiempo total (min)",
            min_value=0.0,
            value=float(comp["objetivo_tiempo_min"] or 0),
            step=1.0,
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
                comp["id"],
                nombre,
                fecha,
                tipo,
                distancia,
                prioridad,
                objetivo_tiempo_min,
                notas,
                activa,
            )

            st.success("Competición actualizada.")

    st.warning("Zona peligrosa")

    if st.button("Borrar competición"):
        eliminar_competicion(comp["id"])
        st.success("Competición eliminada.")
        st.rerun()

from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st

from ui.app_state import get_datos
from data_store.storage import (
    cargar_perfil,
    guardar_perfil,
    cargar_peso,
    guardar_peso,
    cargar_alimentos,
    guardar_alimento,
    cargar_diario,
    guardar_comida,
    cargar_favoritos,
    guardar_favorito,
    registrar_favorito,
    buscar_openfoodfacts,
)

from core.training_metrics import calcular_objetivos_dinamicos
from core.nutrition_metrics import (
    sugerir_comidas_para_macros,
    generar_cena_sugerida,
    generar_menu_restante,
)


def render():
    df, salud = get_datos()
    perfil = cargar_perfil()

    st.title("🍽️ Nutrición")

    with st.expander("⚙️ Perfil y objetivos", expanded=False):
        with st.form("perfil_usuario"):
            peso = st.number_input(
                "Peso actual (kg)", value=float(perfil["peso"]), step=0.1
            )
            altura = st.number_input(
                "Altura (cm)", value=float(perfil["altura"]), step=1.0
            )
            edad = st.number_input("Edad", value=int(perfil["edad"]), step=1)
            superavit = st.number_input(
                "Superávit kcal", value=int(perfil["superavit"]), step=50
            )

            swim_target = st.number_input(
                "Objetivo natación 1500 m",
                value=float(perfil["target_swim_min"]),
                step=1.0,
            )
            bike_target = st.number_input(
                "Objetivo bici 40 km", value=float(perfil["target_bike_min"]), step=1.0
            )
            run_target = st.number_input(
                "Objetivo carrera 10 km",
                value=float(perfil["target_run_min"]),
                step=1.0,
            )

            if st.form_submit_button("Guardar perfil"):
                guardar_perfil(
                    peso, altura, edad, superavit, swim_target, bike_target, run_target
                )
                st.success("Perfil actualizado.")

    st.subheader("⚖️ Peso")

    with st.form("form_peso"):
        fecha_peso = st.date_input("Fecha", value=date.today())
        peso_nuevo = st.number_input(
            "Peso registrado", value=float(perfil["peso"]), step=0.1
        )

        if st.form_submit_button("Guardar peso"):
            guardar_peso(fecha_peso, peso_nuevo)
            st.success("Peso guardado.")

    peso_hist = cargar_peso()

    if not peso_hist.empty:
        fig_peso = px.line(
            peso_hist.sort_values("fecha"),
            x="fecha",
            y="peso",
            markers=True,
            title="Histórico de peso",
        )
        st.plotly_chart(fig_peso, use_container_width=True)

    st.divider()

    st.subheader("🎯 Objetivos dinámicos del día")

    fecha_objetivo = st.date_input(
        "Día", value=date.today(), key="fecha_objetivo_macros"
    )

    objetivos = calcular_objetivos_dinamicos(
        perfil["peso"],
        perfil["altura"],
        perfil["edad"],
        salud,
        df,
        fecha_objetivo,
        perfil["superavit"],
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔥 Kcal", objetivos["calorias"])
    c2.metric("🥩 Proteína", f"{objetivos['proteina']} g")
    c3.metric("🍚 Carbos", f"{objetivos['carbos']} g")
    c4.metric("🥑 Grasas", f"{objetivos['grasas']} g")

    st.caption(
        f"BMR: {objetivos['bmr']} kcal | "
        f"Mantenimiento: {objetivos['mantenimiento']} kcal | "
        f"Kcal entreno: {objetivos['kcal_entreno']}"
    )

    st.divider()

    st.subheader("➕ Añadir alimento")

    metodo = st.radio("Método", ["Manual", "Código de barras"], horizontal=True)

    if metodo == "Manual":
        with st.form("form_alimento_manual"):
            nombre = st.text_input("Nombre")
            kcal = st.number_input("Kcal / 100 g", min_value=0.0)
            proteina = st.number_input("Proteína / 100 g", min_value=0.0)
            carbos = st.number_input("Carbos / 100 g", min_value=0.0)
            grasas = st.number_input("Grasas / 100 g", min_value=0.0)

            if st.form_submit_button("Guardar alimento"):
                if nombre.strip():
                    guardar_alimento(nombre, "", kcal, proteina, carbos, grasas)
                    st.success("Alimento guardado.")
                else:
                    st.error("Introduce un nombre.")

    else:
        barcode = st.text_input("Código de barras")

        if st.button("Buscar producto"):
            producto = buscar_openfoodfacts(barcode)

            if producto:
                guardar_alimento(
                    producto["nombre"],
                    producto["barcode"],
                    producto["kcal_100g"],
                    producto["proteina_100g"],
                    producto["carbos_100g"],
                    producto["grasas_100g"],
                )
                st.success("Producto importado.")
                st.write(producto)
            else:
                st.error("No encontrado.")

    alimentos = cargar_alimentos()

    with st.expander("📋 Base de alimentos"):
        st.dataframe(alimentos, use_container_width=True)

    st.divider()

    st.subheader("🍴 Registrar comida")

    if alimentos.empty:
        st.info("Primero añade alimentos.")
    else:
        with st.form("form_registrar_comida"):
            fecha_comida = st.date_input("Fecha", value=date.today())
            comida = st.selectbox(
                "Comida",
                ["Desayuno", "Media mañana", "Comida", "Merienda", "Cena", "Snack"],
            )
            alimento = st.selectbox("Alimento", alimentos["nombre"].tolist())
            gramos = st.number_input("Cantidad en gramos", min_value=1.0, value=100.0)

            if st.form_submit_button("Registrar comida"):
                fila = alimentos[alimentos["nombre"] == alimento].iloc[0]
                factor = gramos / 100

                guardar_comida(
                    fecha_comida,
                    comida,
                    alimento,
                    gramos,
                    round(float(fila["kcal_100g"]) * factor, 1),
                    round(float(fila["proteina_100g"]) * factor, 1),
                    round(float(fila["carbos_100g"]) * factor, 1),
                    round(float(fila["grasas_100g"]) * factor, 1),
                )

                st.success("Comida registrada.")

    st.divider()

    st.subheader("⭐ Favoritos")

    favoritos = cargar_favoritos()

    if not alimentos.empty:
        with st.form("form_crear_favorito"):
            nombre_fav = st.text_input("Nombre favorito")
            comida_fav = st.selectbox(
                "Comida",
                ["Desayuno", "Media mañana", "Comida", "Merienda", "Cena", "Snack"],
                key="fav_comida",
            )
            alimento_fav = st.selectbox(
                "Alimento", alimentos["nombre"].tolist(), key="fav_alimento"
            )
            gramos_fav = st.number_input(
                "Gramos", min_value=1.0, value=100.0, key="fav_gramos"
            )

            if st.form_submit_button("Añadir favorito"):
                if nombre_fav.strip():
                    guardar_favorito(nombre_fav, comida_fav, alimento_fav, gramos_fav)
                    st.success("Favorito guardado.")

    favoritos = cargar_favoritos()

    if not favoritos.empty:
        st.dataframe(favoritos, use_container_width=True)

        with st.form("form_registrar_favorito"):
            fav_elegido = st.selectbox(
                "Registrar favorito", favoritos["nombre_favorito"].unique()
            )
            fecha_fav = st.date_input("Fecha", value=date.today(), key="fecha_fav")

            if st.form_submit_button("Registrar favorito"):
                if registrar_favorito(fav_elegido, fecha_fav):
                    st.success("Favorito registrado.")
                else:
                    st.error("No se pudo registrar.")

    st.divider()

    st.subheader("📊 Consumo diario")

    diario = cargar_diario()
    fecha_ver = st.date_input("Ver día", value=date.today(), key="fecha_ver_nutricion")
    diario_dia = diario[diario["fecha"] == fecha_ver]

    if diario_dia.empty:
        st.info("No hay comidas registradas para este día.")
        return

    total_kcal = diario_dia["kcal"].sum()
    total_proteina = diario_dia["proteina"].sum()
    total_carbos = diario_dia["carbos"].sum()
    total_grasas = diario_dia["grasas"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔥 Kcal", f"{round(total_kcal)} / {objetivos['calorias']}")
    c2.metric("🥩 Proteína", f"{round(total_proteina)} / {objetivos['proteina']} g")
    c3.metric("🍚 Carbos", f"{round(total_carbos)} / {objetivos['carbos']} g")
    c4.metric("🥑 Grasas", f"{round(total_grasas)} / {objetivos['grasas']} g")

    st.dataframe(diario_dia, use_container_width=True)

    kcal_faltan = max(objetivos["calorias"] - total_kcal, 0)
    proteina_falta = max(objetivos["proteina"] - total_proteina, 0)
    carbos_faltan = max(objetivos["carbos"] - total_carbos, 0)
    grasas_faltan = max(objetivos["grasas"] - total_grasas, 0)

    st.write(
        f"Faltan aprox: **{round(kcal_faltan)} kcal**, "
        f"**{round(proteina_falta)} g proteína**, "
        f"**{round(carbos_faltan)} g carbos**, "
        f"**{round(grasas_faltan)} g grasas**."
    )

    sugerencias = sugerir_comidas_para_macros(
        alimentos,
        kcal_faltan,
        proteina_falta,
        carbos_faltan,
        grasas_faltan,
    )

    if not sugerencias.empty:
        st.subheader("Sugerencias")
        st.dataframe(sugerencias, use_container_width=True)

    cena = generar_cena_sugerida(
        alimentos,
        kcal_faltan,
        proteina_falta,
        carbos_faltan,
        grasas_faltan,
    )

    if not cena.empty:
        st.subheader("Comida/cena sugerida")
        st.dataframe(cena, use_container_width=True)

    menu = generar_menu_restante(
        alimentos,
        kcal_faltan,
        proteina_falta,
        carbos_faltan,
        grasas_faltan,
    )

    if not menu.empty:
        st.subheader("Menú recomendado")
        st.dataframe(menu, use_container_width=True)

    progreso = pd.DataFrame(
        [
            {
                "Macro": "Kcal",
                "Consumido": total_kcal,
                "Objetivo": objetivos["calorias"],
            },
            {
                "Macro": "Proteína",
                "Consumido": total_proteina,
                "Objetivo": objetivos["proteina"],
            },
            {
                "Macro": "Carbos",
                "Consumido": total_carbos,
                "Objetivo": objetivos["carbos"],
            },
            {
                "Macro": "Grasas",
                "Consumido": total_grasas,
                "Objetivo": objetivos["grasas"],
            },
        ]
    )

    fig = px.bar(
        progreso,
        x="Macro",
        y=["Consumido", "Objetivo"],
        barmode="group",
        title="Consumo vs objetivo",
    )

    st.plotly_chart(fig, use_container_width=True)

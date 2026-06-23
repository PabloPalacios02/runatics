from datetime import date

import pandas as pd
import streamlit as st

from ui.theme import aplicar_estilos, hero
from ui.app_state import get_datos
from ui.cards import metric_card
from ui.charts import grafica_peso, grafica_consumo_vs_objetivo

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
    aplicar_estilos()

    df, salud = get_datos()
    perfil = cargar_perfil()

    hero("Nutrición", "Controla tus macros, calorías, peso y alimentación diaria.")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Hoy", "Registrar comida", "Alimentos", "Favoritos", "Peso y perfil"]
    )

    with tab1:
        mostrar_resumen_hoy(df, salud, perfil)

    with tab2:
        mostrar_registro_comida()

    with tab3:
        mostrar_alimentos()

    with tab4:
        mostrar_favoritos()

    with tab5:
        mostrar_peso_y_perfil(perfil)


def obtener_objetivos(df, salud, perfil, fecha_objetivo):
    return calcular_objetivos_dinamicos(
        perfil["peso"],
        perfil["altura"],
        perfil["edad"],
        salud,
        df,
        fecha_objetivo,
        perfil["superavit"],
    )


def mostrar_resumen_hoy(df, salud, perfil):
    st.subheader("Resumen del día")

    fecha_ver = st.date_input(
        "Día",
        value=date.today(),
        key="nutricion_fecha_resumen",
    )

    objetivos = obtener_objetivos(df, salud, perfil, fecha_ver)

    diario = cargar_diario()
    diario_dia = diario[diario["fecha"] == fecha_ver]

    total_kcal = diario_dia["kcal"].sum() if not diario_dia.empty else 0
    total_proteina = diario_dia["proteina"].sum() if not diario_dia.empty else 0
    total_carbos = diario_dia["carbos"].sum() if not diario_dia.empty else 0
    total_grasas = diario_dia["grasas"].sum() if not diario_dia.empty else 0

    c1, c2, c3, c4 = st.columns(4)

    metric_card(c1, "🔥 Kcal", f"{round(total_kcal)} / {objetivos['calorias']}")
    metric_card(
        c2, "🥩 Proteína", f"{round(total_proteina)} / {objetivos['proteina']} g"
    )
    metric_card(c3, "🍚 Carbos", f"{round(total_carbos)} / {objetivos['carbos']} g")
    metric_card(c4, "🥑 Grasas", f"{round(total_grasas)} / {objetivos['grasas']} g")

    st.caption(
        f"BMR: {objetivos['bmr']} kcal | "
        f"Mantenimiento: {objetivos['mantenimiento']} kcal | "
        f"Kcal entreno: {objetivos['kcal_entreno']}"
    )

    if diario_dia.empty:
        st.info("No hay comidas registradas para este día.")
        return

    st.dataframe(diario_dia, use_container_width=True, hide_index=True)

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

    grafica_consumo_vs_objetivo(progreso)

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

    alimentos = cargar_alimentos()

    if alimentos.empty:
        st.info("Añade alimentos para generar sugerencias.")
        return

    with st.expander("Sugerencias para completar macros"):
        sugerencias = sugerir_comidas_para_macros(
            alimentos,
            kcal_faltan,
            proteina_falta,
            carbos_faltan,
            grasas_faltan,
        )

        if sugerencias.empty:
            st.info("No hay suficientes alimentos para generar sugerencias.")
        else:
            st.dataframe(sugerencias, use_container_width=True, hide_index=True)

    with st.expander("Comida/cena sugerida"):
        cena = generar_cena_sugerida(
            alimentos,
            kcal_faltan,
            proteina_falta,
            carbos_faltan,
            grasas_faltan,
        )

        if cena.empty:
            st.info("No se pudo generar una comida completa.")
        else:
            st.dataframe(cena, use_container_width=True, hide_index=True)

    with st.expander("Menú recomendado"):
        menu = generar_menu_restante(
            alimentos,
            kcal_faltan,
            proteina_falta,
            carbos_faltan,
            grasas_faltan,
        )

        if menu.empty:
            st.info("No se pudo generar un menú completo.")
        else:
            st.dataframe(menu, use_container_width=True, hide_index=True)


def mostrar_registro_comida():
    st.subheader("Registrar comida")

    alimentos = cargar_alimentos()

    if alimentos.empty:
        st.info("Primero añade alimentos en la pestaña Alimentos.")
        return

    with st.form("form_registrar_comida"):
        fecha_comida = st.date_input("Fecha", value=date.today())
        comida = st.selectbox(
            "Comida",
            ["Desayuno", "Media mañana", "Comida", "Merienda", "Cena", "Snack"],
        )
        alimento = st.selectbox("Alimento", alimentos["nombre"].tolist())
        gramos = st.number_input("Cantidad en gramos", min_value=1.0, value=100.0)

        registrar = st.form_submit_button("Registrar comida")

        if registrar:
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

    diario = cargar_diario()
    diario_hoy = diario[diario["fecha"] == date.today()]

    if not diario_hoy.empty:
        st.subheader("Comidas registradas hoy")
        st.dataframe(diario_hoy, use_container_width=True, hide_index=True)


def mostrar_alimentos():
    st.subheader("Base de alimentos")

    metodo = st.radio(
        "Método para añadir alimento",
        ["Manual", "Código de barras"],
        horizontal=True,
    )

    if metodo == "Manual":
        with st.form("form_alimento_manual"):
            nombre = st.text_input("Nombre del alimento")
            kcal = st.number_input("Kcal / 100 g", min_value=0.0)
            proteina = st.number_input("Proteína / 100 g", min_value=0.0)
            carbos = st.number_input("Carbos / 100 g", min_value=0.0)
            grasas = st.number_input("Grasas / 100 g", min_value=0.0)

            guardar = st.form_submit_button("Guardar alimento")

            if guardar:
                if not nombre.strip():
                    st.error("Introduce un nombre.")
                else:
                    guardar_alimento(nombre, "", kcal, proteina, carbos, grasas)
                    st.success("Alimento guardado.")

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
                st.error("No se encontró el producto.")

    alimentos = cargar_alimentos()

    st.subheader("Alimentos guardados")

    if alimentos.empty:
        st.info("Todavía no tienes alimentos guardados.")
    else:
        st.dataframe(alimentos, use_container_width=True, hide_index=True)


def mostrar_favoritos():
    st.subheader("Comidas favoritas")

    alimentos = cargar_alimentos()

    if alimentos.empty:
        st.info("Primero añade alimentos.")
        return

    with st.form("form_crear_favorito"):
        nombre_fav = st.text_input(
            "Nombre del favorito",
            placeholder="Ej: Desayuno avena + proteína",
        )

        comida_fav = st.selectbox(
            "Comida",
            ["Desayuno", "Media mañana", "Comida", "Merienda", "Cena", "Snack"],
            key="fav_comida",
        )

        alimento_fav = st.selectbox(
            "Alimento",
            alimentos["nombre"].tolist(),
            key="fav_alimento",
        )

        gramos_fav = st.number_input(
            "Gramos",
            min_value=1.0,
            value=100.0,
            key="fav_gramos",
        )

        guardar = st.form_submit_button("Añadir alimento al favorito")

        if guardar:
            if not nombre_fav.strip():
                st.error("Introduce un nombre.")
            else:
                guardar_favorito(nombre_fav, comida_fav, alimento_fav, gramos_fav)
                st.success("Favorito guardado.")

    favoritos = cargar_favoritos()

    if favoritos.empty:
        st.info("Aún no hay favoritos.")
        return

    st.dataframe(favoritos, use_container_width=True, hide_index=True)

    with st.form("form_registrar_favorito"):
        fav_elegido = st.selectbox(
            "Registrar favorito",
            favoritos["nombre_favorito"].unique().tolist(),
        )

        fecha_fav = st.date_input(
            "Fecha",
            value=date.today(),
            key="fecha_fav",
        )

        registrar = st.form_submit_button("Registrar favorito")

        if registrar:
            ok = registrar_favorito(fav_elegido, fecha_fav)

            if ok:
                st.success("Favorito registrado.")
            else:
                st.error("No se pudo registrar.")


def mostrar_peso_y_perfil(perfil):
    st.subheader("Peso")

    with st.form("form_peso"):
        fecha_peso = st.date_input("Fecha", value=date.today())
        peso_nuevo = st.number_input(
            "Peso registrado (kg)",
            value=float(perfil["peso"]),
            step=0.1,
        )

        guardar = st.form_submit_button("Guardar peso")

        if guardar:
            guardar_peso(fecha_peso, peso_nuevo)
            st.success("Peso guardado.")

    peso_hist = cargar_peso()

    if not peso_hist.empty:
        peso_hist = peso_hist.sort_values("fecha")

        peso_actual = peso_hist.iloc[-1]["peso"]
        peso_inicial = peso_hist.iloc[0]["peso"]
        diferencia = round(float(peso_actual) - float(peso_inicial), 2)

        c1, c2, c3 = st.columns(3)
        metric_card(c1, "Peso inicial", f"{float(peso_inicial):.1f} kg")
        metric_card(c2, "Peso actual", f"{float(peso_actual):.1f} kg")
        metric_card(c3, "Cambio", f"{diferencia:+} kg")

        grafica_peso(peso_hist)

    st.divider()

    st.subheader("Perfil y objetivos")

    with st.form("perfil_usuario"):
        peso = st.number_input(
            "Peso actual (kg)",
            value=float(perfil["peso"]),
            step=0.1,
        )

        altura = st.number_input(
            "Altura (cm)",
            value=float(perfil["altura"]),
            step=1.0,
        )

        edad = st.number_input(
            "Edad",
            value=int(perfil["edad"]),
            step=1,
        )

        superavit = st.number_input(
            "Superávit para ganar masa (kcal)",
            value=int(perfil["superavit"]),
            step=50,
        )

        st.markdown("### Objetivos triatlón")

        swim_target = st.number_input(
            "Objetivo natación 1500 m (min)",
            value=float(perfil["target_swim_min"]),
            step=1.0,
        )

        bike_target = st.number_input(
            "Objetivo bici 40 km (min)",
            value=float(perfil["target_bike_min"]),
            step=1.0,
        )

        run_target = st.number_input(
            "Objetivo carrera 10 km (min)",
            value=float(perfil["target_run_min"]),
            step=1.0,
        )

        guardar = st.form_submit_button("Guardar perfil")

        if guardar:
            guardar_perfil(
                peso,
                altura,
                edad,
                superavit,
                swim_target,
                bike_target,
                run_target,
            )
            st.success("Perfil actualizado.")

import os
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from config.settings import APP_TITLE, APP_CAPTION, OBJETIVO_FECHA
from services.strava_service import cargar_strava
from services.garmin_service import login_garmin, cargar_garmin_actividades, obtener_salud_garmin
from core.activity_merge import fusionar_actividades
from core.training_metrics import (
    generar_recomendaciones, calcular_objetivos_dinamicos, generar_entrenamiento_detallado,
    analizar_cumplimiento_entrenos, predictor_inteligente, replanificar_semana_real,
    calcular_recovery_score
)
from core.nutrition_metrics import sugerir_comidas_para_macros, generar_cena_sugerida, generar_menu_restante
from core.ai_coach import preguntar_coach_ia
from data_store.storage import (
    configurar_directorio_usuario, set_user_data_dir, cargar_alimentos, guardar_alimento,
    cargar_diario, guardar_comida, buscar_openfoodfacts, cargar_perfil, guardar_perfil,
    cargar_peso, guardar_peso, cargar_favoritos, guardar_favorito, registrar_favorito
)

st.set_page_config(page_title="Garmin + Strava Dashboard", page_icon="🏊", layout="wide")

st.title(APP_TITLE)
st.caption(APP_CAPTION)

set_user_data_dir(st.session_state.get("garmin_user_id", "default"))

# ---------------- SIDEBAR ----------------

st.sidebar.header("🔐 Garmin Connect")

email = st.sidebar.text_input("Email Garmin")
password = st.sidebar.text_input("Contraseña Garmin", type="password")

if st.sidebar.button("🚪 Cerrar sesión"):
    st.session_state.clear()
    st.rerun()

hoy = date.today()
inicio_default = hoy - timedelta(days=90)

rango = st.sidebar.date_input("Rango de fechas", value=(inicio_default, hoy))

# ---------------- STRAVA ----------------










# ---------------- GARMIN ----------------












# ---------------- FUSIÓN ----------------




# ---------------- RECOMENDACIONES ----------------




# ---------------- CARGA DATOS ----------------

if st.sidebar.button("Cargar Garmin + Strava"):
    if not email or not password:
        st.error("Introduce email y contraseña de Garmin.")
        st.stop()

    if isinstance(rango, tuple) and len(rango) == 2:
        inicio, fin = rango
    else:
        inicio, fin = inicio_default, hoy

    try:
        with st.spinner("Cargando Garmin y Strava..."):
            client = login_garmin(email, password)

            perfil_garmin = client.get_user_profile()
            user_id = perfil_garmin.get("id", "default")

            st.session_state["perfil_garmin"] = perfil_garmin
            st.session_state["garmin_user_id"] = user_id
            st.session_state["DATA_DIR"] = configurar_directorio_usuario(user_id)

            DATA_DIR = st.session_state["DATA_DIR"]

            ALIMENTOS_PATH = os.path.join(DATA_DIR, "alimentos.csv")
            DIARIO_PATH = os.path.join(DATA_DIR, "diario_comidas.csv")
            PERFIL_PATH = os.path.join(DATA_DIR, "perfil_usuario.csv")
            PESO_PATH = os.path.join(DATA_DIR, "peso.csv")
            FAVORITOS_PATH = os.path.join(DATA_DIR, "comidas_favoritas.csv")

            df_garmin = cargar_garmin_actividades(client, inicio, fin)
            salud = obtener_salud_garmin(client, dias=21)

            df_strava = cargar_strava(inicio, fin)

            df_total = fusionar_actividades(df_garmin, df_strava)

        st.session_state["df"] = df_total
        st.session_state["salud"] = salud
        st.session_state["df_garmin"] = df_garmin
        st.session_state["df_strava"] = df_strava

        st.success(
            f"Datos cargados: Garmin {len(df_garmin)} actividades | "
            f"Strava {len(df_strava)} actividades | "
            f"Total sin duplicados {len(df_total)}"
        )

    except Exception as e:
        st.error(f"Error cargando datos: {e}")

if "garmin_user_id" in st.session_state:
    st.sidebar.success(f"Usuario activo: {st.session_state['garmin_user_id']}")

if "df" not in st.session_state:
    st.info("Introduce Garmin, selecciona rango y pulsa **Cargar Garmin + Strava**.")
    st.stop()

df = st.session_state["df"]
salud = st.session_state["salud"]

if df.empty:
    st.warning("No hay actividades para mostrar.")
    st.stop()












# ---------------- PERFIL Y PLANIFICACIÓN ----------------












# ---------------- PESO, FAVORITOS, PREDICTOR Y PLAN AVANZADO ----------------






















# ---------------- SUGERENCIAS DE COMIDA Y REPLANIFICACIÓN ----------------






# ---------------- REPLANIFICACIÓN, PREDICTOR Y NUTRICIÓN INTELIGENTE ----------------














# ---------------- GEMINI COACH IA ----------------








# ---------------- TABS ----------------

tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "🏠 Hoy",
        "📊 Resumen",
        "📋 Actividades",
        "❤️ Salud Garmin",
        "🧠 Recomendaciones",
        "📅 Planificador",
        "🍽️ Nutrición",
        "🤖 Coach IA",
    ]
)

with tab0:
    st.subheader("🏠 Resumen de hoy")

    perfil = cargar_perfil()
    objetivos_hoy = calcular_objetivos_dinamicos(
        perfil["peso"],
        perfil["altura"],
        perfil["edad"],
        salud,
        df,
        date.today(),
        perfil["superavit"],
    )

    plan, pred, fase, recuperacion_baja = generar_entrenamiento_detallado(
        df, salud, perfil
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🔥 Kcal objetivo hoy", objetivos_hoy["calorias"])
    c2.metric("🥩 Proteína", f"{objetivos_hoy['proteina']} g")
    c3.metric("🍚 Carbos", f"{objetivos_hoy['carbos']} g")
    c4.metric("🥑 Grasas", f"{objetivos_hoy['grasas']} g")

    st.write(f"📍 Fase actual: **{fase}**")
    st.write(f"📅 Días hasta el triatlón: **{(OBJETIVO_FECHA - hoy).days}**")

    if recuperacion_baja:
        st.warning("Recuperación baja: hoy conviene reducir intensidad.")
    else:
        st.success("Recuperación correcta: puedes entrenar normal.")

    st.subheader("🎯 Predicción actual")

    st.write(f"🏊 1500 m natación: **{pred['swim_1500_min']} min**")
    st.write(f"🚴 40 km bici: **{pred['bike_40k_min']} min**")
    st.write(f"🏃 10 km carrera: **{pred['run_10k_min']} min**")
    st.write(
        f"⏱️ Total estimado sin transiciones: **{pred['total_estimado_min']} min**"
    )

    st.subheader("📌 Entreno recomendado")
    st.dataframe(plan.head(1), use_container_width=True)

with tab1:
    st.subheader("📊 Resumen del periodo")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric(
        "🏃 Km running", round(df[df["deporte"] == "Running"]["distancia_km"].sum(), 1)
    )
    c2.metric("🚴 Km bici", round(df[df["deporte"] == "Bici"]["distancia_km"].sum(), 1))
    c3.metric(
        "🏊 Km natación",
        round(df[df["deporte"] == "Natación"]["distancia_km"].sum(), 2),
    )
    c4.metric("🏋️ Gym sesiones", len(df[df["deporte"] == "Gimnasio"]))
    c5.metric("⏱️ Horas totales", round(df["duracion_min"].sum() / 60, 1))

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            df.groupby("deporte", as_index=False)["duracion_min"].sum(),
            x="deporte",
            y="duracion_min",
            color="deporte",
            title="Tiempo por deporte",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.line(
            df.sort_values("fecha"),
            x="fecha",
            y="distancia_km",
            color="deporte",
            markers=True,
            title="Distancia por día",
        )
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("📋 Actividades fusionadas Garmin + Strava")

    st.dataframe(df, use_container_width=True)

    st.write("Origen de datos:")
    st.dataframe(df["origen"].value_counts().reset_index(), use_container_width=True)

with tab3:
    st.subheader("❤️ Salud Garmin")

    st.dataframe(salud, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        if salud["sleep_hours"].notna().any():
            fig = px.line(
                salud, x="fecha", y="sleep_hours", markers=True, title="Sueño"
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        if salud["resting_hr"].notna().any():
            fig = px.line(
                salud, x="fecha", y="resting_hr", markers=True, title="FC reposo"
            )
            st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("🧠 Recomendaciones automáticas")

    for r in generar_recomendaciones(df, salud):
        st.write(r)

with tab5:
    st.subheader("📅 Planificador inteligente detallado")

    perfil = cargar_perfil()
    plan, pred, fase, recuperacion_baja = generar_entrenamiento_detallado(
        df, salud, perfil
    )

    cumplimiento = analizar_cumplimiento_entrenos(df)
    pred, gaps, tendencias = predictor_inteligente(df, salud, perfil)
    plan = replanificar_semana_real(plan, cumplimiento, gaps, recuperacion_baja)
    recovery_score, recovery_estado = calcular_recovery_score(salud, df)

    st.write(f"Fase actual de preparación: **{fase}**")
    st.write(f"Objetivo: **Triatlón olímpico - 27 septiembre 2026**")

    c1, c2, c3 = st.columns(3)
    c1.metric("🏊 Objetivo 1500 m", f"{perfil['target_swim_min']} min")
    c2.metric("🚴 Objetivo 40 km", f"{perfil['target_bike_min']} min")
    c3.metric("🏃 Objetivo 10 km", f"{perfil['target_run_min']} min")

    st.subheader("📈 Predictor avanzado")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏊 Pred. 1500 m", f"{pred['swim_1500_min']} min")
    c2.metric("🚴 Pred. 40 km", f"{pred['bike_40k_min']} min")
    c3.metric("🏃 Pred. 10 km", f"{pred['run_10k_min']} min")
    c4.metric("⏱️ Total", f"{pred['total_estimado_min']} min")

    st.subheader("🧬 Recuperación Garmin")

    c1, c2 = st.columns(2)
    c1.metric("Recovery Score", f"{recovery_score}/100")
    c2.metric("Estado", recovery_estado)

    st.subheader("🎯 Objetivo vs predicción")
    st.dataframe(gaps, use_container_width=True)

    st.subheader("📊 Tendencia últimos 90 días")
    st.dataframe(tendencias, use_container_width=True)

    st.subheader("🔍 Actividades usadas para la predicción")

    detalles = []

    if pred["detalle_swim"]:
        detalles.append(
            {
                "Disciplina": "Natación",
                "Actividad": pred["detalle_swim"]["actividad"],
                "Fecha": pred["detalle_swim"]["fecha"],
                "Distancia": pred["detalle_swim"]["distancia"],
                "Dato clave": f"{pred['detalle_swim']['ritmo_100m']} min/100m",
            }
        )

    if pred["detalle_bike"]:
        detalles.append(
            {
                "Disciplina": "Bici",
                "Actividad": pred["detalle_bike"]["actividad"],
                "Fecha": pred["detalle_bike"]["fecha"],
                "Distancia": pred["detalle_bike"]["distancia"],
                "Dato clave": f"{pred['detalle_bike']['speed_kmh']} km/h",
            }
        )

    if pred["detalle_run"]:
        detalles.append(
            {
                "Disciplina": "Running",
                "Actividad": pred["detalle_run"]["actividad"],
                "Fecha": pred["detalle_run"]["fecha"],
                "Distancia": pred["detalle_run"]["distancia"],
                "Dato clave": f"{pred['detalle_run']['pace_min_km']} min/km",
            }
        )

    if detalles:
        st.dataframe(pd.DataFrame(detalles), use_container_width=True)
    else:
        st.info(
            "Aún no hay suficientes actividades para generar una predicción completa."
        )

    if recuperacion_baja:
        st.warning("La planificación se ha suavizado por sueño bajo o estrés alto.")
    else:
        st.success("Planificación normal.")

    st.subheader("📈 Cumplimiento últimos 7 días")
    st.dataframe(cumplimiento, use_container_width=True)

    st.subheader("📋 Semana propuesta detallada")
    st.dataframe(plan, use_container_width=True)

with tab6:
    st.subheader("🍽️ Nutrición y macros")

    perfil = cargar_perfil()

    st.subheader("⚙️ Perfil nutricional y objetivos")

    with st.form("perfil_usuario"):
        peso = st.number_input(
            "Peso actual (kg)", value=float(perfil["peso"]), step=0.1
        )
        altura = st.number_input("Altura (cm)", value=float(perfil["altura"]), step=1.0)
        edad = st.number_input("Edad", value=int(perfil["edad"]), step=1)
        superavit = st.number_input(
            "Superávit para ganar masa (kcal)", value=int(perfil["superavit"]), step=50
        )

        st.markdown("### 🎯 Objetivos triatlón")

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
                peso, altura, edad, superavit, swim_target, bike_target, run_target
            )
            st.success("Perfil actualizado correctamente.")

    perfil = cargar_perfil()

    st.divider()

    st.subheader("⚖️ Registro de peso")

    with st.form("form_peso"):
        fecha_peso = st.date_input("Fecha del peso", value=date.today())
        peso_nuevo = st.number_input(
            "Peso registrado (kg)", value=float(perfil["peso"]), step=0.1
        )
        guardar_p = st.form_submit_button("Guardar peso")

        if guardar_p:
            guardar_peso(fecha_peso, peso_nuevo)
            guardar_perfil(
                peso_nuevo,
                perfil["altura"],
                perfil["edad"],
                perfil["superavit"],
                perfil["target_swim_min"],
                perfil["target_bike_min"],
                perfil["target_run_min"],
            )
            st.success("Peso guardado y perfil actualizado.")

    peso_hist = cargar_peso()

    if not peso_hist.empty:
        peso_hist = peso_hist.sort_values("fecha")
        peso_actual = peso_hist.iloc[-1]["peso"]
        peso_inicial = peso_hist.iloc[0]["peso"]
        diferencia = round(peso_actual - peso_inicial, 2)

        st.metric("Cambio de peso registrado", f"{diferencia:+} kg")

        fig_peso = px.line(
            peso_hist, x="fecha", y="peso", markers=True, title="Histórico de peso"
        )
        st.plotly_chart(fig_peso, use_container_width=True)

    st.divider()

    st.subheader("🎯 Objetivos dinámicos del día")

    fecha_objetivo_macros = st.date_input(
        "Calcular macros para el día", value=date.today(), key="fecha_objetivo_macros"
    )

    objetivos = calcular_objetivos_dinamicos(
        perfil["peso"],
        perfil["altura"],
        perfil["edad"],
        salud,
        df,
        fecha_objetivo_macros,
        perfil["superavit"],
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🔥 Kcal objetivo", objetivos["calorias"])
    c2.metric("🥩 Proteína", f"{objetivos['proteina']} g")
    c3.metric("🍚 Carbohidratos", f"{objetivos['carbos']} g")
    c4.metric("🥑 Grasas", f"{objetivos['grasas']} g")

    st.caption(
        f"BMR estimado: {objetivos['bmr']} kcal | "
        f"Mantenimiento estimado según actividad/Garmin: {objetivos['mantenimiento']} kcal"
    )

    st.divider()

    st.subheader("➕ Añadir alimento a la base de datos")

    metodo = st.radio("Método", ["Manual", "Código de barras"], horizontal=True)

    if metodo == "Manual":
        with st.form("form_alimento_manual"):
            nombre = st.text_input("Nombre del alimento")
            kcal = st.number_input("Kcal / 100 g", min_value=0.0)
            proteina = st.number_input("Proteína / 100 g", min_value=0.0)
            carbos = st.number_input("Carbohidratos / 100 g", min_value=0.0)
            grasas = st.number_input("Grasas / 100 g", min_value=0.0)

            enviar = st.form_submit_button("Guardar alimento")

            if enviar:
                if nombre.strip() == "":
                    st.error("Introduce un nombre para el alimento.")
                else:
                    guardar_alimento(nombre, "", kcal, proteina, carbos, grasas)
                    st.success("Alimento guardado correctamente.")

    else:
        st.info(
            "Desde móvil puedes escanear el código con cualquier app de escáner "
            "y pegarlo aquí. La cámara integrada la añadiremos en la fase APK/WebView."
        )

        barcode = st.text_input("Código de barras")

        if st.button("Buscar producto"):
            producto = buscar_openfoodfacts(barcode)

            if producto:
                st.write(producto)

                guardar_alimento(
                    producto["nombre"],
                    producto["barcode"],
                    producto["kcal_100g"],
                    producto["proteina_100g"],
                    producto["carbos_100g"],
                    producto["grasas_100g"],
                )

                st.success("Producto importado y guardado.")
            else:
                st.error("No se encontró el producto.")

    st.divider()

    st.subheader("📋 Base de alimentos")

    alimentos = cargar_alimentos()
    st.dataframe(alimentos, use_container_width=True)

    st.divider()

    st.subheader("🍴 Registrar comida")

    if alimentos.empty:
        st.info("Primero añade alimentos a la base de datos.")
    else:
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

                kcal = round(fila["kcal_100g"] * factor, 1)
                proteina = round(fila["proteina_100g"] * factor, 1)
                carbos = round(fila["carbos_100g"] * factor, 1)
                grasas = round(fila["grasas_100g"] * factor, 1)

                guardar_comida(
                    fecha_comida,
                    comida,
                    alimento,
                    gramos,
                    kcal,
                    proteina,
                    carbos,
                    grasas,
                )

                st.success("Comida registrada.")

    st.divider()

    st.subheader("⭐ Comidas favoritas")

    favoritos = cargar_favoritos()

    if not alimentos.empty:
        with st.form("form_crear_favorito"):
            nombre_fav = st.text_input(
                "Nombre del favorito", placeholder="Ej: Desayuno avena + proteína"
            )

            comida_fav = st.selectbox(
                "Comida del favorito",
                ["Desayuno", "Media mañana", "Comida", "Merienda", "Cena", "Snack"],
            )

            alimento_fav = st.selectbox(
                "Alimento favorito", alimentos["nombre"].tolist(), key="fav_alimento"
            )

            gramos_fav = st.number_input(
                "Gramos", min_value=1.0, value=100.0, key="fav_gramos"
            )

            guardar_fav = st.form_submit_button("Añadir alimento al favorito")

            if guardar_fav:
                if nombre_fav.strip() == "":
                    st.error("Introduce un nombre para el favorito.")
                else:
                    guardar_favorito(nombre_fav, comida_fav, alimento_fav, gramos_fav)
                    st.success("Alimento añadido al favorito.")

    favoritos = cargar_favoritos()

    if not favoritos.empty:
        st.dataframe(favoritos, use_container_width=True)

        favs_disponibles = favoritos["nombre_favorito"].unique().tolist()

        with st.form("form_registrar_favorito"):
            fav_elegido = st.selectbox("Registrar favorito", favs_disponibles)
            fecha_fav = st.date_input("Fecha", value=date.today(), key="fecha_fav")
            registrar_fav = st.form_submit_button("Registrar comida favorita")

            if registrar_fav:
                ok = registrar_favorito(fav_elegido, fecha_fav)

                if ok:
                    st.success("Favorito registrado correctamente.")
                else:
                    st.error("No se pudo registrar el favorito.")
    else:
        st.info("Aún no hay comidas favoritas guardadas.")

    st.divider()

    st.subheader("📊 Consumo diario")

    diario = cargar_diario()
    fecha_ver = st.date_input("Ver día", value=date.today(), key="fecha_ver_nutricion")

    diario_dia = diario[diario["fecha"] == fecha_ver]

    objetivos_dia = calcular_objetivos_dinamicos(
        perfil["peso"],
        perfil["altura"],
        perfil["edad"],
        salud,
        df,
        fecha_ver,
        perfil["superavit"],
    )

    if diario_dia.empty:
        st.info("No hay comidas registradas para este día.")
    else:
        total_kcal = diario_dia["kcal"].sum()
        total_proteina = diario_dia["proteina"].sum()
        total_carbos = diario_dia["carbos"].sum()
        total_grasas = diario_dia["grasas"].sum()

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("🔥 Kcal", f"{round(total_kcal)} / {objetivos_dia['calorias']}")
        c2.metric(
            "🥩 Proteína", f"{round(total_proteina)} / {objetivos_dia['proteina']} g"
        )
        c3.metric("🍚 Carbos", f"{round(total_carbos)} / {objetivos_dia['carbos']} g")
        c4.metric("🥑 Grasas", f"{round(total_grasas)} / {objetivos_dia['grasas']} g")

        st.dataframe(diario_dia, use_container_width=True)

        st.subheader("🍽️ Sugerencias para completar macros")

        kcal_faltan = max(objetivos_dia["calorias"] - total_kcal, 0)
        proteina_falta = max(objetivos_dia["proteina"] - total_proteina, 0)
        carbos_faltan = max(objetivos_dia["carbos"] - total_carbos, 0)
        grasas_faltan = max(objetivos_dia["grasas"] - total_grasas, 0)

        st.write(
            f"Te faltan aproximadamente: "
            f"**{round(kcal_faltan)} kcal**, "
            f"**{round(proteina_falta)} g proteína**, "
            f"**{round(carbos_faltan)} g carbos**, "
            f"**{round(grasas_faltan)} g grasas**."
        )

        sugerencias = sugerir_comidas_para_macros(
            alimentos, kcal_faltan, proteina_falta, carbos_faltan, grasas_faltan
        )

        if sugerencias.empty:
            st.info("No hay suficientes alimentos en tu base para generar sugerencias.")
        else:
            st.dataframe(sugerencias, use_container_width=True)

        st.subheader("🍽️ Comida/cena sugerida")

        cena_sugerida = generar_cena_sugerida(
            alimentos, kcal_faltan, proteina_falta, carbos_faltan, grasas_faltan
        )

        if cena_sugerida.empty:
            st.info("No se pudo generar una comida completa con tu base actual.")
        else:
            st.dataframe(cena_sugerida, use_container_width=True)

            st.write(
                f"Total sugerido: "
                f"**{round(cena_sugerida['Kcal'].sum())} kcal**, "
                f"**{round(cena_sugerida['Proteína'].sum(), 1)} g proteína**, "
                f"**{round(cena_sugerida['Carbos'].sum(), 1)} g carbos**, "
                f"**{round(cena_sugerida['Grasas'].sum(), 1)} g grasas**."
            )

        st.subheader("📋 Menú recomendado para completar el día")

        menu_restante = generar_menu_restante(
            alimentos,
            kcal_faltan,
            proteina_falta,
            carbos_faltan,
            grasas_faltan,
        )

        if menu_restante.empty:
            st.info("No se pudo generar un menú completo con la base actual.")
        else:
            st.dataframe(menu_restante, use_container_width=True)

            st.write(
                f"Total menú: "
                f"**{round(menu_restante['Kcal'].sum())} kcal**, "
                f"**{round(menu_restante['Proteína'].sum(), 1)} g proteína**, "
                f"**{round(menu_restante['Carbos'].sum(), 1)} g carbos**, "
                f"**{round(menu_restante['Grasas'].sum(), 1)} g grasas**."
            )

        progreso = pd.DataFrame(
            [
                {
                    "Macro": "Kcal",
                    "Consumido": total_kcal,
                    "Objetivo": objetivos_dia["calorias"],
                },
                {
                    "Macro": "Proteína",
                    "Consumido": total_proteina,
                    "Objetivo": objetivos_dia["proteina"],
                },
                {
                    "Macro": "Carbos",
                    "Consumido": total_carbos,
                    "Objetivo": objetivos_dia["carbos"],
                },
                {
                    "Macro": "Grasas",
                    "Consumido": total_grasas,
                    "Objetivo": objetivos_dia["grasas"],
                },
            ]
        )

        fig = px.bar(
            progreso,
            x="Macro",
            y=["Consumido", "Objetivo"],
            barmode="group",
            title="Consumo vs objetivo dinámico",
        )

        st.plotly_chart(fig, use_container_width=True)

with tab7:

    st.subheader("🤖 Coach IA")

    perfil = cargar_perfil()

    pregunta = st.text_area(
        "Pregunta al entrenador", placeholder="Ejemplo: ¿Qué debería entrenar mañana?"
    )

    if st.button("Preguntar al coach"):

        if pregunta.strip():

            with st.spinner("Analizando tus datos..."):

                try:
                    respuesta = preguntar_coach_ia(pregunta, df, salud, perfil)

                    st.markdown(respuesta)

                except Exception as e:
                    st.error(f"Error: {e}")
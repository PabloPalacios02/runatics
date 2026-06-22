from datetime import date, timedelta
import pandas as pd
from config.settings import OBJETIVO_FECHA

def generar_recomendaciones(df, salud):
    recomendaciones = []

    ult7 = df[df["fecha"].dt.date >= date.today() - timedelta(days=7)]

    km_run = ult7[ult7["deporte"] == "Running"]["distancia_km"].sum()
    km_bici = ult7[ult7["deporte"] == "Bici"]["distancia_km"].sum()
    km_nat = ult7[ult7["deporte"] == "Natación"]["distancia_km"].sum()
    sesiones_gym = len(ult7[ult7["deporte"] == "Gimnasio"])
    horas = ult7["duracion_min"].sum() / 60

    sleep_avg = salud["sleep_hours"].dropna().tail(7).mean()
    resting_avg = salud["resting_hr"].dropna().tail(7).mean()
    stress_avg = salud["stress"].dropna().tail(7).mean()
    vo2 = salud["vo2max"].dropna().tail(1)

    dias_restantes = (OBJETIVO_FECHA - date.today()).days

    recomendaciones.append(
        f"🎯 Quedan **{dias_restantes} días** para el triatlón olímpico."
    )

    if pd.notna(sleep_avg):
        if sleep_avg < 6.5:
            recomendaciones.append(
                "😴 Sueño bajo: baja intensidad y prioriza recuperación."
            )
        elif sleep_avg >= 7.5:
            recomendaciones.append("✅ Buen sueño: puedes asimilar carga.")
        else:
            recomendaciones.append("🟡 Sueño aceptable, intenta acercarte a 7.5–8 h.")

    if pd.notna(resting_avg):
        recomendaciones.append(f"❤️ FC reposo media: **{round(resting_avg)} bpm**.")

    if pd.notna(stress_avg):
        if stress_avg > 45:
            recomendaciones.append("⚠️ Estrés alto: evita encadenar sesiones duras.")
        else:
            recomendaciones.append("✅ Estrés controlado.")

    if not vo2.empty:
        recomendaciones.append(f"🫁 VO2max registrado: **{vo2.iloc[-1]}**.")

    if km_nat < 3:
        recomendaciones.append(
            "🏊 Natación insuficiente: prioriza frecuencia y técnica."
        )
    else:
        recomendaciones.append("✅ Natación bien encaminada.")

    if km_bici < 50:
        recomendaciones.append("🚴 Bici baja para olímpico: mete 2 sesiones semanales.")
    else:
        recomendaciones.append("✅ Volumen de bici aceptable.")

    if km_run < 8:
        recomendaciones.append(
            "🏃 Running bajo: mantén 1 sesión semanal de calidad o controlada."
        )
    elif km_run > 25:
        recomendaciones.append("⚠️ Running alto: cuidado con fatiga acumulada.")
    else:
        recomendaciones.append("✅ Running equilibrado.")

    if sesiones_gym < 3:
        recomendaciones.append(
            "🏋️ Gimnasio bajo para masa muscular: intenta 3 sesiones mínimo."
        )
    else:
        recomendaciones.append("✅ Gimnasio bien cubierto.")

    if horas > 9:
        recomendaciones.append("⚠️ Carga alta: mete 1 día real de descanso.")
    elif horas < 5:
        recomendaciones.append("📈 Carga baja: puedes progresar ligeramente.")
    else:
        recomendaciones.append("✅ Carga semanal razonable.")

    return recomendaciones


def fase_preparacion():
    dias = (OBJETIVO_FECHA - date.today()).days

    if dias > 90:
        return "Base"
    elif dias > 45:
        return "Construcción"
    elif dias > 14:
        return "Específica"
    else:
        return "Puesta a punto"


def calcular_objetivos_dinamicos(
    peso, altura, edad, salud, df, fecha_objetivo=date.today(), superavit=300
):
    # Mifflin-St Jeor hombre
    bmr = 10 * peso + 6.25 * altura - 5 * edad + 5

    actividades_dia = df[df["fecha"].dt.date == fecha_objetivo]

    kcal_entreno = actividades_dia["calorias"].dropna().sum()

    # Si Garmin/Strava no tiene calorías fiables, estimamos por minutos y deporte
    if kcal_entreno == 0 and not actividades_dia.empty:
        for _, act in actividades_dia.iterrows():
            dur = act["duracion_min"] if pd.notna(act["duracion_min"]) else 0
            dep = act["deporte"]

            if dep == "Running":
                kcal_entreno += dur * 11
            elif dep == "Bici":
                kcal_entreno += dur * 8
            elif dep == "Natación":
                kcal_entreno += dur * 9
            elif dep == "Gimnasio":
                kcal_entreno += dur * 6
            else:
                kcal_entreno += dur * 5

    # Base diaria sin contar entrenamiento formal
    # Para ti: estudiante activo + pasos + vida diaria
    mantenimiento_base = bmr * 1.45

    # Mantenimiento real del día
    mantenimiento = mantenimiento_base + kcal_entreno

    # Superávit para ganar masa muscular
    calorias = mantenimiento + superavit

    # Proteína alta pero realista
    proteina = peso * 2.1

    # Grasas saludables mínimas
    grasas = peso * 1.0

    kcal_proteina = proteina * 4
    kcal_grasas = grasas * 9

    carbos = (calorias - kcal_proteina - kcal_grasas) / 4

    return {
        "calorias": round(calorias),
        "proteina": round(proteina),
        "carbos": round(max(carbos, 0)),
        "grasas": round(grasas),
        "mantenimiento": round(mantenimiento),
        "bmr": round(bmr),
        "kcal_entreno": round(kcal_entreno),
    }


def mejor_rendimiento_running(df):
    run = df[
        (df["deporte"] == "Running")
        & (df["distancia_km"] >= 5)
        & (df["ritmo_min_km"].notna())
    ].copy()

    if run.empty:
        return None

    run["score"] = run["ritmo_min_km"] - (run["distancia_km"] * 0.015)
    mejor = run.sort_values("score").iloc[0]

    pace = mejor["ritmo_min_km"]

    return {
        "pace_min_km": round(pace, 2),
        "pred_10k": round(pace * 10, 1),
        "actividad": mejor["nombre"],
        "fecha": mejor["fecha"],
        "distancia": mejor["distancia_km"],
    }


def mejor_rendimiento_bici(df):
    bike = df[
        (df["deporte"] == "Bici")
        & (df["distancia_km"] >= 15)
        & (df["velocidad_kmh"].notna())
    ].copy()

    if bike.empty:
        return None

    bike["score"] = bike["velocidad_kmh"] + (bike["distancia_km"] * 0.03)
    mejor = bike.sort_values("score", ascending=False).iloc[0]

    speed = mejor["velocidad_kmh"]

    return {
        "speed_kmh": round(speed, 2),
        "pred_40k": round(40 / speed * 60, 1),
        "actividad": mejor["nombre"],
        "fecha": mejor["fecha"],
        "distancia": mejor["distancia_km"],
    }


def mejor_rendimiento_natacion(df):
    swim = df[
        (df["deporte"] == "Natación")
        & (df["distancia_km"] >= 0.5)
        & (df["duracion_min"].notna())
    ].copy()

    if swim.empty:
        return None

    swim["ritmo_min_100m"] = swim["duracion_min"] / (swim["distancia_km"] * 10)
    mejor = swim.sort_values("ritmo_min_100m").iloc[0]

    ritmo_100 = mejor["ritmo_min_100m"]

    return {
        "ritmo_100m": round(ritmo_100, 2),
        "pred_1500": round(ritmo_100 * 15, 1),
        "actividad": mejor["nombre"],
        "fecha": mejor["fecha"],
        "distancia": mejor["distancia_km"],
    }


def estimar_prediccion_triatlon_avanzada(df):
    recientes = df[df["fecha"].dt.date >= date.today() - timedelta(days=90)]

    r = mejor_rendimiento_running(recientes)
    b = mejor_rendimiento_bici(recientes)
    n = mejor_rendimiento_natacion(recientes)

    swim = n["pred_1500"] if n else None
    bike = b["pred_40k"] if b else None
    run = r["pred_10k"] if r else None

    total = sum(x for x in [swim, bike, run] if x is not None)

    return {
        "swim_1500_min": swim,
        "bike_40k_min": bike,
        "run_10k_min": run,
        "total_estimado_min": round(total, 1),
        "detalle_run": r,
        "detalle_bike": b,
        "detalle_swim": n,
    }


def generar_entrenamiento_detallado(df, salud, perfil):
    fase = fase_preparacion()
    pred = estimar_prediccion_triatlon_avanzada(df)

    sleep_avg = salud["sleep_hours"].dropna().tail(7).mean()
    stress_avg = salud["stress"].dropna().tail(7).mean()

    recuperacion_baja = (pd.notna(sleep_avg) and sleep_avg < 6.5) or (
        pd.notna(stress_avg) and stress_avg > 45
    )

    run_target_pace = perfil["target_run_min"] / 10
    bike_target_speed = 40 / (perfil["target_bike_min"] / 60)
    swim_target_100 = perfil["target_swim_min"] / 15

    if fase == "Base":
        swim_main = "Técnica + volumen suave"
        bike_main = "Z2 cómoda"
        run_main = "Rodaje controlado"
        gym_main = "Hipertrofia controlada"
    elif fase == "Construcción":
        swim_main = "Técnica + bloques a ritmo"
        bike_main = "Bloques tempo"
        run_main = "Tempo/series suaves"
        gym_main = "Fuerza + hipertrofia"
    elif fase == "Específica":
        swim_main = "Ritmo objetivo 1500 m"
        bike_main = "Ritmo objetivo 40 km"
        run_main = "Ritmo objetivo 10 km"
        gym_main = "Fuerza mantenimiento"
    else:
        swim_main = "Afinar técnica"
        bike_main = "Activación corta"
        run_main = "Activación corta"
        gym_main = "Muy ligero"

    if recuperacion_baja:
        intensidad = "Reducida"
        factor = 0.75
    else:
        intensidad = "Normal"
        factor = 1.0

    plan = [
        {
            "Día": "Lunes",
            "Sesión": "Natación + Gimnasio torso",
            "Entrenamiento detallado": f"Natación 1200–1800 m: 300 m suave + 6x50 técnica + 4x100 a {round(swim_target_100 + 0.15, 2)} min/100m + 200 m suave. Gimnasio torso 60 min.",
            "Objetivo": swim_main + " + " + gym_main,
            "Intensidad": intensidad,
        },
        {
            "Día": "Martes",
            "Sesión": "Bici calidad",
            "Entrenamiento detallado": f"Bici {round(45*factor)}–{round(70*factor)} min: 10 min suave + 3x8 min a {round(bike_target_speed*0.85, 1)}–{round(bike_target_speed*0.95, 1)} km/h + 5–10 min suave.",
            "Objetivo": bike_main,
            "Intensidad": intensidad,
        },
        {
            "Día": "Miércoles",
            "Sesión": "Natación + Gimnasio pierna",
            "Entrenamiento detallado": f"Natación 1000–1500 m suave/técnica. Gimnasio pierna 50–60 min: sentadilla/hack, rumano, zancadas, gemelo. Sin llegar al fallo.",
            "Objetivo": swim_main + " + fuerza pierna",
            "Intensidad": intensidad,
        },
        {
            "Día": "Jueves",
            "Sesión": "Running calidad",
            "Entrenamiento detallado": f"Running {round(7*factor)}–{round(11*factor)} km: 2 km suave + 4x1 km a {round(run_target_pace + 0.15, 2)}–{round(run_target_pace + 0.30, 2)} min/km + recuperación 2 min + 1 km suave.",
            "Objetivo": run_main,
            "Intensidad": "Media-alta" if not recuperacion_baja else "Media",
        },
        {
            "Día": "Viernes",
            "Sesión": "Natación + Gimnasio full body",
            "Entrenamiento detallado": f"Natación 1200–1600 m: 200 suave + 8x100 ritmo controlado + 200 suave. Full body 45–60 min.",
            "Objetivo": "Frecuencia de agua + fuerza global",
            "Intensidad": intensidad,
        },
        {
            "Día": "Sábado",
            "Sesión": "Bici larga + transición",
            "Entrenamiento detallado": f"Bici {round(75*factor)}–{round(120*factor)} min Z2/Z3 suave. Cadencia 85–95 rpm. Opcional: 10–15 min trote a ritmo cómodo después.",
            "Objetivo": "Resistencia específica triatlón",
            "Intensidad": "Media",
        },
        {
            "Día": "Domingo",
            "Sesión": "Natación suave / descanso",
            "Entrenamiento detallado": "Si estás bien: 800–1200 m técnica suave. Si estás cargado: descanso completo + movilidad 15 min.",
            "Objetivo": "Recuperación activa",
            "Intensidad": "Baja",
        },
    ]

    return pd.DataFrame(plan), pred, fase, recuperacion_baja


def analizar_cumplimiento_entrenos(df):
    ult7 = df[df["fecha"].dt.date >= date.today() - timedelta(days=7)]

    sesiones_natacion = len(ult7[ult7["deporte"] == "Natación"])
    sesiones_bici = len(ult7[ult7["deporte"] == "Bici"])
    sesiones_running = len(ult7[ult7["deporte"] == "Running"])
    sesiones_gym = len(ult7[ult7["deporte"] == "Gimnasio"])

    objetivo = {
        "Natación": 5,
        "Bici": 2,
        "Running": 1,
        "Gimnasio": 3,
    }

    real = {
        "Natación": sesiones_natacion,
        "Bici": sesiones_bici,
        "Running": sesiones_running,
        "Gimnasio": sesiones_gym,
    }

    filas = []

    for deporte in objetivo:
        porcentaje = round((real[deporte] / objetivo[deporte]) * 100, 1)

        if porcentaje < 70:
            estado = "Bajo"
        elif porcentaje > 130:
            estado = "Exceso"
        else:
            estado = "Correcto"

        filas.append(
            {
                "Disciplina": deporte,
                "Objetivo semanal": objetivo[deporte],
                "Realizado": real[deporte],
                "Cumplimiento %": porcentaje,
                "Estado": estado,
            }
        )

    return pd.DataFrame(filas)


def calcular_gaps_objetivo(pred, perfil):
    gaps = []

    objetivos = {
        "Natación": ("swim_1500_min", perfil["target_swim_min"]),
        "Bici": ("bike_40k_min", perfil["target_bike_min"]),
        "Running": ("run_10k_min", perfil["target_run_min"]),
    }

    for deporte, (clave, objetivo) in objetivos.items():
        prediccion = pred.get(clave)

        if prediccion is None:
            gap = None
            estado = "Sin datos"
        else:
            gap = round(prediccion - objetivo, 1)

            if gap <= 0:
                estado = "Objetivo alcanzable"
            elif gap <= objetivo * 0.08:
                estado = "Cerca"
            else:
                estado = "Lejos"

        gaps.append(
            {
                "Disciplina": deporte,
                "Objetivo min": objetivo,
                "Predicción min": prediccion,
                "Diferencia min": gap,
                "Estado": estado,
            }
        )

    return pd.DataFrame(gaps)


def replanificar_semana_real(plan, cumplimiento, gaps, recuperacion_baja):
    plan = plan.copy()

    bajos = cumplimiento[cumplimiento["Estado"] == "Bajo"]["Disciplina"].tolist()
    excesos = cumplimiento[cumplimiento["Estado"] == "Exceso"]["Disciplina"].tolist()

    disciplina_prioritaria = None

    gaps_validos = gaps.dropna(subset=["Diferencia min"])
    gaps_validos = gaps_validos[gaps_validos["Diferencia min"] > 0]

    if not gaps_validos.empty:
        disciplina_prioritaria = gaps_validos.sort_values(
            "Diferencia min", ascending=False
        ).iloc[0]["Disciplina"]

    ajustes = []

    if recuperacion_baja:
        ajustes.append("Recuperación baja: reducir volumen e intensidad esta semana.")

    if disciplina_prioritaria:
        ajustes.append(f"Prioridad de rendimiento: {disciplina_prioritaria}.")

    for dep in bajos:
        ajustes.append(f"Compensar falta de {dep}.")

    for dep in excesos:
        ajustes.append(f"Reducir ligeramente {dep} para evitar sobrecarga.")

    if not ajustes:
        ajustes.append("Semana equilibrada: mantener progresión.")

    plan["Ajuste automático"] = " | ".join(ajustes)

    # Cambios reales en sesiones según prioridad
    if disciplina_prioritaria == "Natación" or "Natación" in bajos:
        plan.loc[plan["Día"] == "Domingo", "Sesión"] = "Natación técnica extra"
        plan.loc[plan["Día"] == "Domingo", "Entrenamiento detallado"] = (
            "Natación 1000–1400 m técnica: 300 m suave + 8x50 técnica + "
            "4x100 ritmo cómodo + 200 m suave."
        )
        plan.loc[plan["Día"] == "Domingo", "Objetivo"] = "Compensar falta de natación"

    if disciplina_prioritaria == "Bici" or "Bici" in bajos:
        plan.loc[plan["Día"] == "Martes", "Entrenamiento detallado"] = (
            "Bici 60–75 min: 10 min suave + 4x8 min tempo controlado "
            "+ 5–10 min suave. Priorizar cadencia estable 85–95 rpm."
        )
        plan.loc[plan["Día"] == "Sábado", "Entrenamiento detallado"] = (
            "Bici larga 100–130 min Z2/Z3 suave + transición opcional "
            "10 min trote cómodo."
        )

    if disciplina_prioritaria == "Running" or "Running" in bajos:
        plan.loc[plan["Día"] == "Jueves", "Entrenamiento detallado"] = (
            "Running calidad: 2 km suave + 5x1 km a ritmo objetivo controlado "
            "+ recuperación 2 min + 1 km suave."
        )

    if "Running" in excesos:
        plan.loc[plan["Día"] == "Jueves", "Entrenamiento detallado"] = (
            "Running suave 6–8 km en Z2. Sin series esta semana."
        )
        plan.loc[plan["Día"] == "Jueves", "Intensidad"] = "Baja-media"

    if "Gimnasio" in bajos:
        plan.loc[
            plan["Día"] == "Domingo", "Entrenamiento detallado"
        ] += " + Core/movilidad 15–20 min."

    if recuperacion_baja:
        plan["Entrenamiento detallado"] = (
            plan["Entrenamiento detallado"]
            .str.replace("5x1 km", "3x1 km", regex=False)
            .str.replace("4x8 min", "3x6 min", regex=False)
        )

    return plan


def predictor_inteligente(df, salud, perfil):
    pred_base = estimar_prediccion_triatlon_avanzada(df)
    gaps = calcular_gaps_objetivo(pred_base, perfil)

    recientes_90 = df[df["fecha"].dt.date >= date.today() - timedelta(days=90)]
    recientes_28 = df[df["fecha"].dt.date >= date.today() - timedelta(days=28)]

    resumen = []
    pred_ajustada = pred_base.copy()

    vo2_series = salud["vo2max"].dropna()
    vo2 = vo2_series.iloc[-1] if not vo2_series.empty else None

    sleep_avg = salud["sleep_hours"].dropna().tail(7).mean()
    stress_avg = salud["stress"].dropna().tail(7).mean()
    resting_avg = salud["resting_hr"].dropna().tail(7).mean()

    penalizacion_recuperacion = 1.0
    if pd.notna(sleep_avg) and sleep_avg < 6.5:
        penalizacion_recuperacion += 0.04
    if pd.notna(stress_avg) and stress_avg > 45:
        penalizacion_recuperacion += 0.03

    for deporte in ["Natación", "Bici", "Running"]:
        datos_90 = recientes_90[recientes_90["deporte"] == deporte].sort_values("fecha")
        datos_28 = recientes_28[recientes_28["deporte"] == deporte].sort_values("fecha")

        sesiones_28 = len(datos_28)
        sesiones_90 = len(datos_90)

        if deporte == "Running":
            clave = "run_10k_min"
            media_28 = (
                datos_28["ritmo_min_km"].dropna().mean() * 10
                if sesiones_28 > 0
                else None
            )
        elif deporte == "Bici":
            clave = "bike_40k_min"
            vel_28 = datos_28["velocidad_kmh"].dropna().mean()
            media_28 = 40 / vel_28 * 60 if pd.notna(vel_28) and vel_28 > 0 else None
        else:
            clave = "swim_1500_min"
            datos_swim = datos_28[datos_28["distancia_km"] > 0]
            media_28 = (
                (datos_swim["duracion_min"] / (datos_swim["distancia_km"] * 10)).mean()
                * 15
                if not datos_swim.empty
                else None
            )

        mejor = pred_base.get(clave)

        if mejor is not None and media_28 is not None:
            estimacion = mejor * 0.45 + media_28 * 0.45
        elif mejor is not None:
            estimacion = mejor
        elif media_28 is not None:
            estimacion = media_28
        else:
            estimacion = None

        if estimacion is not None:
            if sesiones_28 < 2:
                estimacion *= 1.06
            elif sesiones_28 >= 5:
                estimacion *= 0.98

            estimacion *= penalizacion_recuperacion

            if deporte == "Running" and vo2 is not None:
                if vo2 >= 55:
                    estimacion *= 0.97
                elif vo2 < 45:
                    estimacion *= 1.04

            pred_ajustada[clave] = round(estimacion, 1)

        if sesiones_90 < 2:
            tendencia = "Sin datos suficientes"
        else:
            primera = datos_90.head(max(1, sesiones_90 // 2))
            segunda = datos_90.tail(max(1, sesiones_90 // 2))

            if deporte == "Running":
                antes = primera["ritmo_min_km"].dropna().mean()
                ahora = segunda["ritmo_min_km"].dropna().mean()
                mejora = antes - ahora if pd.notna(antes) and pd.notna(ahora) else None
            elif deporte == "Bici":
                antes = primera["velocidad_kmh"].dropna().mean()
                ahora = segunda["velocidad_kmh"].dropna().mean()
                mejora = ahora - antes if pd.notna(antes) and pd.notna(ahora) else None
            else:
                primera = primera[primera["distancia_km"] > 0]
                segunda = segunda[segunda["distancia_km"] > 0]
                antes = (
                    primera["duracion_min"] / (primera["distancia_km"] * 10)
                ).mean()
                ahora = (
                    segunda["duracion_min"] / (segunda["distancia_km"] * 10)
                ).mean()
                mejora = antes - ahora if pd.notna(antes) and pd.notna(ahora) else None

            if mejora is None:
                tendencia = "Sin tendencia clara"
            elif mejora > 0:
                tendencia = "Mejorando"
            elif mejora < 0:
                tendencia = "Empeorando"
            else:
                tendencia = "Estable"

        resumen.append(
            {
                "Disciplina": deporte,
                "Tendencia": tendencia,
                "Sesiones 28 días": sesiones_28,
                "Sesiones 90 días": sesiones_90,
                "Km 90 días": round(datos_90["distancia_km"].sum(), 1),
            }
        )

    total = sum(
        x
        for x in [
            pred_ajustada.get("swim_1500_min"),
            pred_ajustada.get("bike_40k_min"),
            pred_ajustada.get("run_10k_min"),
        ]
        if x is not None
    )

    pred_ajustada["total_estimado_min"] = round(total, 1)
    gaps = calcular_gaps_objetivo(pred_ajustada, perfil)

    return pred_ajustada, gaps, pd.DataFrame(resumen)


def calcular_recovery_score(salud, df):
    score = 100

    sleep_avg = salud["sleep_hours"].dropna().tail(7).mean()
    stress_avg = salud["stress"].dropna().tail(7).mean()
    resting = salud["resting_hr"].dropna().tail(7)
    ult7 = df[df["fecha"].dt.date >= date.today() - timedelta(days=7)]
    horas_7 = ult7["duracion_min"].sum() / 60

    if pd.notna(sleep_avg):
        if sleep_avg < 6:
            score -= 25
        elif sleep_avg < 7:
            score -= 12

    if pd.notna(stress_avg):
        if stress_avg > 55:
            score -= 20
        elif stress_avg > 45:
            score -= 10

    if len(resting) >= 4:
        if resting.iloc[-1] > resting.mean() + 5:
            score -= 15

    if horas_7 > 10:
        score -= 15
    elif horas_7 < 3:
        score -= 5

    score = max(min(score, 100), 0)

    if score >= 80:
        estado = "Alta recuperación"
    elif score >= 60:
        estado = "Recuperación aceptable"
    else:
        estado = "Recuperación baja"

    return score, estado

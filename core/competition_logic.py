from datetime import date


def dias_hasta(comp):
    if comp is None:
        return None
    return (comp["fecha"] - date.today()).days


def fase_por_competicion(comp):
    if comp is None:
        return "General"

    dias = dias_hasta(comp)

    if dias is None:
        return "General"
    if dias > 90:
        return "Base"
    if dias > 45:
        return "Construcción"
    if dias > 14:
        return "Específica"
    return "Puesta a punto"


def resumen_competicion(comp):
    if comp is None:
        return "Sin competición principal"

    distancia = comp.get("distancia", "")
    km = comp.get("distancia_km", 0)

    if km and km > 0:
        distancia_txt = f"{distancia} · {km:g} km"
    else:
        distancia_txt = distancia

    return f"{comp['nombre']} · {comp['tipo']} · {distancia_txt}"


def enfoque_planificacion(comp_principal, secundarias):
    if comp_principal is None:
        return "Plan general equilibrado de resistencia, fuerza y recuperación."

    tipo = str(comp_principal.get("tipo", "")).lower()
    distancia = str(comp_principal.get("distancia", "")).lower()

    enfoque = []

    if "triatlón" in tipo or "triatlon" in tipo:
        enfoque.append("Priorizar equilibrio entre natación, bici, carrera y fuerza.")
        if "olímpico" in distancia or "olimpico" in distancia:
            enfoque.append(
                "Mantener frecuencia alta de natación y bici, con carrera controlada."
            )
        elif "sprint" in distancia:
            enfoque.append("Trabajar intensidad corta y transiciones.")
        elif "ironman" in distancia:
            enfoque.append("Priorizar volumen aeróbico y gestión de fatiga.")

    elif "running" in tipo:
        enfoque.append(
            "Priorizar carrera, técnica, rodajes y una sesión de calidad semanal."
        )

    elif "ciclismo" in tipo:
        enfoque.append("Priorizar volumen de bici, cadencia y fuerza de piernas.")

    elif "natación" in tipo or "natacion" in tipo:
        enfoque.append("Priorizar frecuencia en agua, técnica y ritmo específico.")

    else:
        enfoque.append("Plan general adaptado a la competición principal.")

    if secundarias is not None and not secundarias.empty:
        proximas = secundarias.head(3)["nombre"].tolist()
        enfoque.append(
            "Competiciones secundarias próximas: " + ", ".join(proximas) + "."
        )

    return " ".join(enfoque)


def adaptar_plan_a_competiciones(
    plan, comp_principal, secundarias, recuperacion_baja=False
):
    plan = plan.copy()

    if comp_principal is None:
        plan["Adaptación competición"] = "Plan general sin competición principal."
        return plan

    tipo = str(comp_principal.get("tipo", "")).lower()
    distancia = str(comp_principal.get("distancia", "")).lower()
    distancia_km = float(comp_principal.get("distancia_km") or 0)
    dias = dias_hasta(comp_principal)

    ajustes = []

    # =========================
    # TRIATLÓN
    # =========================
    if "triatlón" in tipo or "triatlon" in tipo:
        ajustes.append(
            "Plan adaptado a triatlón: equilibrio natación, bici, carrera y fuerza."
        )

        if "sprint" in distancia:
            ajustes.append("Distancia sprint: más intensidad corta y transiciones.")
            plan.loc[plan["Día"] == "Martes", "Sesión"] = "Bici intensidad + transición"
            plan.loc[plan["Día"] == "Martes", "Entrenamiento detallado"] = (
                "Bici 45–60 min con 6x2 min fuertes + transición 10 min carrera suave."
            )

        elif "olímpico" in distancia or "olimpico" in distancia:
            ajustes.append(
                "Distancia olímpica: bloque específico de ritmo y brick semanal."
            )
            plan.loc[plan["Día"] == "Sábado", "Sesión"] = "Brick bici + carrera"
            plan.loc[plan["Día"] == "Sábado", "Entrenamiento detallado"] = (
                "Bici 90–120 min Z2/Z3 + transición 15–25 min carrera cómoda."
            )

        elif "half" in distancia or "ironman" in distancia:
            ajustes.append("Larga distancia: más volumen aeróbico y menor intensidad.")
            plan.loc[plan["Día"] == "Sábado", "Entrenamiento detallado"] = (
                "Bici larga 2–4 h en Z2 + transición muy suave 10–20 min."
            )
            plan.loc[plan["Día"] == "Jueves", "Entrenamiento detallado"] = (
                "Running Z2 8–12 km. Evitar series agresivas esta semana."
            )

    # =========================
    # RUNNING
    # =========================
    elif "running" in tipo:
        ajustes.append(
            "Plan adaptado a running: prioridad a carrera sin abandonar fuerza."
        )

        if distancia_km <= 5:
            plan.loc[plan["Día"] == "Jueves", "Sesión"] = "Series cortas running"
            plan.loc[plan["Día"] == "Jueves", "Entrenamiento detallado"] = (
                "Running: 2 km suave + 8x400 m rápido + recuperación 90 s + 1 km suave."
            )

        elif distancia_km <= 10:
            plan.loc[plan["Día"] == "Jueves", "Sesión"] = "Series 10K"
            plan.loc[plan["Día"] == "Jueves", "Entrenamiento detallado"] = (
                "Running: 2 km suave + 5x1 km a ritmo objetivo 10K + 2 min recuperación + 1 km suave."
            )

        elif distancia_km <= 21.5:
            plan.loc[plan["Día"] == "Jueves", "Sesión"] = "Tempo media distancia"
            plan.loc[plan["Día"] == "Jueves", "Entrenamiento detallado"] = (
                "Running: 2 km suave + 25–35 min tempo controlado + 1–2 km suave."
            )
            plan.loc[plan["Día"] == "Domingo", "Sesión"] = "Tirada larga"
            plan.loc[plan["Día"] == "Domingo", "Entrenamiento detallado"] = (
                "Tirada larga 75–100 min en Z2, sin forzar."
            )

        else:
            plan.loc[plan["Día"] == "Domingo", "Sesión"] = "Tirada larga maratón"
            plan.loc[plan["Día"] == "Domingo", "Entrenamiento detallado"] = (
                "Tirada larga 90–140 min Z2. Priorizar volumen y nutrición."
            )

    # =========================
    # CICLISMO
    # =========================
    elif "ciclismo" in tipo:
        ajustes.append(
            "Plan adaptado a ciclismo: más volumen de bici y fuerza de pierna controlada."
        )

        plan.loc[plan["Día"] == "Martes", "Sesión"] = "Bici calidad"
        plan.loc[plan["Día"] == "Martes", "Entrenamiento detallado"] = (
            "Bici 60–75 min: 4x8 min tempo/umbral controlado + cadencia estable."
        )

        plan.loc[plan["Día"] == "Sábado", "Sesión"] = "Bici larga"
        plan.loc[plan["Día"] == "Sábado", "Entrenamiento detallado"] = (
            "Bici larga 2–3 h Z2. Comer e hidratar como en competición."
        )

    # =========================
    # NATACIÓN
    # =========================
    elif "natación" in tipo or "natacion" in tipo:
        ajustes.append("Plan adaptado a natación: más frecuencia en agua y técnica.")

        plan.loc[plan["Día"] == "Lunes", "Sesión"] = "Natación técnica"
        plan.loc[plan["Día"] == "Lunes", "Entrenamiento detallado"] = (
            "Natación 1600–2200 m: técnica + 8x100 m ritmo controlado."
        )

        plan.loc[plan["Día"] == "Viernes", "Sesión"] = "Natación ritmo"
        plan.loc[plan["Día"] == "Viernes", "Entrenamiento detallado"] = (
            "Natación 1500–2000 m con bloques a ritmo objetivo."
        )

    # =========================
    # SECUNDARIAS
    # =========================
    if secundarias is not None and not secundarias.empty:
        prox = secundarias.sort_values("fecha").head(2)

        for _, comp in prox.iterrows():
            dias_sec = (comp["fecha"] - date.today()).days
            tipo_sec = str(comp["tipo"]).lower()
            nombre_sec = comp["nombre"]

            if 0 <= dias_sec <= 14:
                ajustes.append(
                    f"Competición secundaria próxima: {nombre_sec} en {dias_sec} días."
                )

                if "running" in tipo_sec:
                    plan.loc[plan["Día"] == "Jueves", "Entrenamiento detallado"] = (
                        "Running activación: 20–35 min suave + 4 progresivos. No cargar piernas."
                    )

                elif "ciclismo" in tipo_sec:
                    plan.loc[plan["Día"] == "Sábado", "Entrenamiento detallado"] = (
                        "Bici controlada 60–90 min. Evitar fatiga excesiva antes de la prueba secundaria."
                    )

                elif "triatlón" in tipo_sec or "triatlon" in tipo_sec:
                    plan.loc[plan["Día"] == "Sábado", "Entrenamiento detallado"] = (
                        "Brick corto de activación: bici 45 min + carrera 10 min suave."
                    )

    # =========================
    # TAPER
    # =========================
    if dias is not None and dias <= 14:
        ajustes.append("Puesta a punto: reducir volumen y mantener algo de intensidad.")

        plan["Entrenamiento detallado"] = (
            plan["Entrenamiento detallado"]
            .astype(str)
            .str.replace("120", "80", regex=False)
            .str.replace("100", "70", regex=False)
            .str.replace("90", "60", regex=False)
        )

    if recuperacion_baja:
        ajustes.append("Recuperación baja: reducción extra de volumen e intensidad.")

    plan["Adaptación competición"] = " | ".join(ajustes)

    return plan

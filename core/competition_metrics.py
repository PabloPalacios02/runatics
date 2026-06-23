import pandas as pd


def _to_float(value, default=0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def prediccion_running(df, distancia_km):
    run = df[
        (df["deporte"] == "Running")
        & (df["ritmo_min_km"].notna())
        & (df["distancia_km"] > 0)
    ]

    if run.empty or distancia_km <= 0:
        return None

    ritmo = run.tail(10)["ritmo_min_km"].mean()
    return round(ritmo * distancia_km, 1)


def prediccion_ciclismo(df, distancia_km):
    bici = df[
        (df["deporte"] == "Bici")
        & (df["velocidad_kmh"].notna())
        & (df["velocidad_kmh"] > 0)
    ]

    if bici.empty or distancia_km <= 0:
        return None

    vel = bici.tail(10)["velocidad_kmh"].mean()
    return round((distancia_km / vel) * 60, 1)


def prediccion_natacion(df, distancia_km):
    swim = df[
        (df["deporte"] == "Natación")
        & (df["distancia_km"] > 0)
        & (df["duracion_min"].notna())
    ]

    if swim.empty or distancia_km <= 0:
        return None

    ritmo_100 = (
        swim.tail(10)["duracion_min"] / (swim.tail(10)["distancia_km"] * 10)
    ).mean()
    return round(ritmo_100 * distancia_km * 10, 1)


def predicciones_para_competicion(df, comp, pred_triatlon=None):
    if comp is None:
        return pd.DataFrame()

    tipo = str(comp.get("tipo", "")).lower()
    distancia = str(comp.get("distancia", ""))
    distancia_km = _to_float(comp.get("distancia_km"))

    filas = []

    if "triatlón" in tipo or "triatlon" in tipo:
        swim_pred = pred_triatlon.get("swim_1500_min") if pred_triatlon else None
        bike_pred = pred_triatlon.get("bike_40k_min") if pred_triatlon else None
        run_pred = pred_triatlon.get("run_10k_min") if pred_triatlon else None

        swim_obj = _to_float(comp.get("objetivo_swim_min"))
        bike_obj = _to_float(comp.get("objetivo_bike_min"))
        run_obj = _to_float(comp.get("objetivo_run_min"))

        filas = [
            {
                "Disciplina": "Natación",
                "Distancia": "1500 m",
                "Predicción min": swim_pred,
                "Objetivo min": swim_obj if swim_obj > 0 else None,
            },
            {
                "Disciplina": "Bici",
                "Distancia": "40 km",
                "Predicción min": bike_pred,
                "Objetivo min": bike_obj if bike_obj > 0 else None,
            },
            {
                "Disciplina": "Carrera",
                "Distancia": "10 km",
                "Predicción min": run_pred,
                "Objetivo min": run_obj if run_obj > 0 else None,
            },
        ]

    elif "running" in tipo:
        pred = prediccion_running(df, distancia_km)
        objetivo = _to_float(comp.get("objetivo_tiempo_min"))

        filas = [
            {
                "Disciplina": "Running",
                "Distancia": f"{distancia_km:g} km",
                "Predicción min": pred,
                "Objetivo min": objetivo if objetivo > 0 else None,
            }
        ]

    elif "ciclismo" in tipo:
        pred = prediccion_ciclismo(df, distancia_km)
        objetivo = _to_float(comp.get("objetivo_tiempo_min"))

        filas = [
            {
                "Disciplina": "Ciclismo",
                "Distancia": f"{distancia_km:g} km",
                "Predicción min": pred,
                "Objetivo min": objetivo if objetivo > 0 else None,
            }
        ]

    elif "natación" in tipo or "natacion" in tipo:
        pred = prediccion_natacion(df, distancia_km)
        objetivo = _to_float(comp.get("objetivo_tiempo_min"))

        filas = [
            {
                "Disciplina": "Natación",
                "Distancia": f"{distancia_km:g} km",
                "Predicción min": pred,
                "Objetivo min": objetivo if objetivo > 0 else None,
            }
        ]

    else:
        return pd.DataFrame()

    df_pred = pd.DataFrame(filas)

    if not df_pred.empty:
        df_pred["Diferencia min"] = df_pred.apply(
            lambda r: (
                round(r["Predicción min"] - r["Objetivo min"], 1)
                if pd.notna(r["Predicción min"]) and pd.notna(r["Objetivo min"])
                else None
            ),
            axis=1,
        )

    return df_pred

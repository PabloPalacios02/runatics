import pandas as pd

def fusionar_actividades(df_garmin, df_strava):
    columnas = [
        "fecha",
        "nombre",
        "deporte",
        "tipo_original",
        "distancia_km",
        "duracion_min",
        "ritmo_min_km",
        "velocidad_kmh",
        "fc_media",
        "fc_max",
        "calorias",
        "origen",
    ]

    if df_garmin.empty and df_strava.empty:
        return pd.DataFrame(columns=columnas)

    if df_strava.empty:
        return df_garmin.sort_values("fecha", ascending=False)

    if df_garmin.empty:
        return df_strava.sort_values("fecha", ascending=False)

    df_garmin = df_garmin.copy()
    df_strava = df_strava.copy()

    df_garmin["fecha"] = pd.to_datetime(
        df_garmin["fecha"], errors="coerce"
    ).dt.tz_localize(None)
    df_strava["fecha"] = pd.to_datetime(
        df_strava["fecha"], errors="coerce"
    ).dt.tz_localize(None)

    df_garmin = df_garmin.dropna(subset=["fecha"])
    df_strava = df_strava.dropna(subset=["fecha"])

    # Strava manda porque recoge Garmin + Hevy + actividades manuales
    actividades_finales = [df_strava]

    garmin_no_duplicadas = []

    for _, g in df_garmin.iterrows():
        duplicada = False

        for _, s in df_strava.iterrows():
            misma_fecha = abs((g["fecha"] - s["fecha"]).total_seconds()) <= 180
            mismo_deporte = g["deporte"] == s["deporte"]

            distancia_parecida = (
                abs((g["distancia_km"] or 0) - (s["distancia_km"] or 0)) <= 0.3
            )
            duracion_parecida = (
                abs((g["duracion_min"] or 0) - (s["duracion_min"] or 0)) <= 3
            )

            if (
                misma_fecha
                and mismo_deporte
                and (distancia_parecida or duracion_parecida)
            ):
                duplicada = True
                break

        if not duplicada:
            garmin_no_duplicadas.append(g)

    if garmin_no_duplicadas:
        df_garmin_extra = pd.DataFrame(garmin_no_duplicadas)
        actividades_finales.append(df_garmin_extra)

    df_total = pd.concat(actividades_finales, ignore_index=True)

    return df_total.sort_values("fecha", ascending=False)

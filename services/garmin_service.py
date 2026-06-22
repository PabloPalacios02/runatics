from datetime import date, timedelta
import pandas as pd
from garminconnect import Garmin

def login_garmin(email, password):
    client = Garmin(email, password)
    client.login()
    return client


def normalizar_garmin_deporte(tipo):
    if tipo in ["running", "trail_running", "treadmill_running"]:
        return "Running"
    if tipo in [
        "cycling",
        "road_biking",
        "indoor_cycling",
        "biking",
        "mountain_biking",
    ]:
        return "Bici"
    if tipo in ["swimming", "lap_swimming", "open_water_swimming"]:
        return "Natación"
    if tipo in ["strength_training"]:
        return "Gimnasio"
    return tipo


def convertir_garmin(a):
    tipo = a.get("activityType", {}).get("typeKey", "Otro")
    distancia_km = round((a.get("distance", 0) or 0) / 1000, 2)
    duracion_min = round((a.get("duration", 0) or 0) / 60, 1)

    ritmo_min_km = None
    velocidad_kmh = None

    if distancia_km > 0 and duracion_min > 0:
        ritmo_min_km = round(duracion_min / distancia_km, 2)
        velocidad_kmh = round(distancia_km / (duracion_min / 60), 2)

    return {
        "fecha": a.get("startTimeLocal"),
        "nombre": a.get("activityName", "Sin nombre"),
        "deporte": normalizar_garmin_deporte(tipo),
        "tipo_original": tipo,
        "distancia_km": distancia_km,
        "duracion_min": duracion_min,
        "ritmo_min_km": ritmo_min_km,
        "velocidad_kmh": velocidad_kmh,
        "fc_media": a.get("averageHR"),
        "fc_max": a.get("maxHR"),
        "calorias": a.get("calories"),
        "origen": "Garmin",
    }


def cargar_garmin_actividades(client, inicio, fin):
    inicio_str = inicio.strftime("%Y-%m-%d")
    fin_str = fin.strftime("%Y-%m-%d")

    try:
        actividades = client.get_activities_by_date(inicio_str, fin_str)
    except Exception:
        actividades = []

    df = pd.DataFrame([convertir_garmin(a) for a in actividades])

    if df.empty:
        return df

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])

    return df


def obtener_salud_garmin(client, dias=21):
    datos = []

    for i in range(dias):
        d = date.today() - timedelta(days=i)
        d_str = d.strftime("%Y-%m-%d")

        fila = {
            "fecha": d,
            "sleep_hours": None,
            "resting_hr": None,
            "steps": None,
            "calories": None,
            "stress": None,
            "vo2max": None,
        }

        try:
            summary = client.get_user_summary(d_str)
            fila["steps"] = summary.get("totalSteps")
            fila["calories"] = summary.get("totalKilocalories")
            fila["resting_hr"] = summary.get("restingHeartRate")
            fila["stress"] = summary.get("averageStressLevel")
        except Exception:
            pass

        try:
            sleep = client.get_sleep_data(d_str)
            segundos = sleep.get("dailySleepDTO", {}).get("sleepTimeSeconds")
            if segundos:
                fila["sleep_hours"] = round(segundos / 3600, 2)
        except Exception:
            pass

        try:
            metrics = client.get_max_metrics(d_str)
            if isinstance(metrics, list) and len(metrics) > 0:
                fila["vo2max"] = metrics[0].get("generic", {}).get("vo2Max")
        except Exception:
            pass

        datos.append(fila)

    return pd.DataFrame(datos).sort_values("fecha")

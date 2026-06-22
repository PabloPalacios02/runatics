from datetime import timedelta
import pandas as pd
import requests
from config.settings import cargar_secrets

secrets = cargar_secrets()

def obtener_strava_access_token():
    url = "https://www.strava.com/api/v3/oauth/token"

    payload = {
        "client_id": secrets["STRAVA_CLIENT_ID"],
        "client_secret": secrets["STRAVA_CLIENT_SECRET"],
        "refresh_token": secrets["STRAVA_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }

    r = requests.post(url, data=payload)

    if r.status_code != 200:
        raise Exception(f"Error autenticando Strava: {r.text}")

    return r.json()["access_token"]


def normalizar_strava_deporte(tipo):
    if tipo in ["Run", "TrailRun", "VirtualRun"]:
        return "Running"
    if tipo in ["Ride", "VirtualRide", "MountainBikeRide", "GravelRide"]:
        return "Bici"
    if tipo in ["Swim"]:
        return "Natación"
    if tipo in ["WeightTraining", "Workout"]:
        return "Gimnasio"
    return tipo


def convertir_strava(a):
    distancia_km = round((a.get("distance", 0) or 0) / 1000, 2)
    duracion_min = round((a.get("moving_time", 0) or 0) / 60, 1)

    ritmo_min_km = None
    velocidad_kmh = None

    if distancia_km > 0 and duracion_min > 0:
        ritmo_min_km = round(duracion_min / distancia_km, 2)
        velocidad_kmh = round(distancia_km / (duracion_min / 60), 2)

    tipo = a.get("sport_type") or a.get("type")

    return {
        "fecha": a.get("start_date_local"),
        "nombre": a.get("name"),
        "deporte": normalizar_strava_deporte(tipo),
        "tipo_original": tipo,
        "distancia_km": distancia_km,
        "duracion_min": duracion_min,
        "ritmo_min_km": ritmo_min_km,
        "velocidad_kmh": velocidad_kmh,
        "fc_media": a.get("average_heartrate"),
        "fc_max": a.get("max_heartrate"),
        "calorias": None,
        "origen": "Strava",
    }


def cargar_strava(inicio, fin):
    token = obtener_strava_access_token()

    after = int(pd.Timestamp(inicio).timestamp())
    before = int(pd.Timestamp(fin + timedelta(days=1)).timestamp())

    headers = {"Authorization": f"Bearer {token}"}

    actividades = []
    page = 1

    while True:
        r = requests.get(
            "https://www.strava.com/api/v3/athlete/activities",
            headers=headers,
            params={
                "after": after,
                "before": before,
                "page": page,
                "per_page": 200,
            },
        )

        if r.status_code != 200:
            raise Exception(f"Error descargando Strava: {r.text}")

        lote = r.json()

        if not lote:
            break

        actividades.extend(lote)
        page += 1

        if page > 10:
            break

    df = pd.DataFrame([convertir_strava(a) for a in actividades])

    if df.empty:
        return df

    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])

    return df

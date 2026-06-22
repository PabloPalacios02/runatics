from datetime import date
import pandas as pd
import requests
import streamlit as st

from services.supabase_service import get_supabase_client

# ============================================================
# USUARIO ACTUAL
# ============================================================


def get_current_user_id():
    return str(st.session_state.get("garmin_user_id", "default"))


def configurar_directorio_usuario(user_id):
    """
    Se mantiene por compatibilidad con el app.py antiguo.
    Ya no crea carpetas porque ahora usamos Supabase.
    """
    st.session_state["garmin_user_id"] = str(user_id)
    return str(user_id)


def set_user_data_dir(user_id="default"):
    """
    Se mantiene por compatibilidad.
    """
    st.session_state["garmin_user_id"] = str(user_id)
    return str(user_id)


# ============================================================
# HELPERS SUPABASE
# ============================================================


def _client():
    return get_supabase_client()


def _to_df(data, columns):
    df = pd.DataFrame(data or [])

    for col in columns:
        if col not in df.columns:
            df[col] = None

    return df[columns]


def _fecha_str(fecha):
    if isinstance(fecha, date):
        return fecha.isoformat()
    return str(fecha)


# ============================================================
# ALIMENTOS
# ============================================================


def cargar_alimentos():
    columnas = [
        "nombre",
        "barcode",
        "kcal_100g",
        "proteina_100g",
        "carbos_100g",
        "grasas_100g",
    ]

    user_id = get_current_user_id()

    res = (
        _client()
        .table("foods")
        .select(",".join(columnas))
        .eq("user_id", user_id)
        .order("nombre")
        .execute()
    )

    return _to_df(res.data, columnas)


def guardar_alimento(nombre, barcode, kcal, proteina, carbos, grasas):
    user_id = get_current_user_id()

    data = {
        "user_id": user_id,
        "nombre": nombre,
        "barcode": barcode,
        "kcal_100g": float(kcal or 0),
        "proteina_100g": float(proteina or 0),
        "carbos_100g": float(carbos or 0),
        "grasas_100g": float(grasas or 0),
    }

    (_client().table("foods").upsert(data, on_conflict="user_id,nombre").execute())


# ============================================================
# DIARIO DE COMIDAS
# ============================================================


def cargar_diario():
    columnas = [
        "fecha",
        "comida",
        "alimento",
        "gramos",
        "kcal",
        "proteina",
        "carbos",
        "grasas",
    ]

    user_id = get_current_user_id()

    res = (
        _client()
        .table("food_logs")
        .select(",".join(columnas))
        .eq("user_id", user_id)
        .order("fecha", desc=True)
        .execute()
    )

    df = _to_df(res.data, columnas)

    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date

    return df


def guardar_comida(fecha, comida, alimento, gramos, kcal, proteina, carbos, grasas):
    user_id = get_current_user_id()

    data = {
        "user_id": user_id,
        "fecha": _fecha_str(fecha),
        "comida": comida,
        "alimento": alimento,
        "gramos": float(gramos or 0),
        "kcal": float(kcal or 0),
        "proteina": float(proteina or 0),
        "carbos": float(carbos or 0),
        "grasas": float(grasas or 0),
    }

    _client().table("food_logs").insert(data).execute()


# ============================================================
# OPEN FOOD FACTS
# ============================================================


def buscar_openfoodfacts(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    r = requests.get(url, timeout=10)

    if r.status_code != 200:
        return None

    data = r.json()

    if data.get("status") != 1:
        return None

    producto = data.get("product", {})
    nutriments = producto.get("nutriments", {})

    return {
        "nombre": producto.get("product_name", "Producto sin nombre"),
        "barcode": barcode,
        "kcal_100g": nutriments.get("energy-kcal_100g", 0),
        "proteina_100g": nutriments.get("proteins_100g", 0),
        "carbos_100g": nutriments.get("carbohydrates_100g", 0),
        "grasas_100g": nutriments.get("fat_100g", 0),
    }


# ============================================================
# PERFIL
# ============================================================


def crear_perfil_desde_garmin(perfil_garmin):
    user_data = perfil_garmin.get("userData", {})

    peso = user_data.get("weight", 71000)
    altura = user_data.get("height", 182)
    birth_date = user_data.get("birthDate")

    if peso and peso > 300:
        peso = peso / 1000

    edad = 23

    if birth_date:
        try:
            nacimiento = pd.to_datetime(birth_date).date()
            hoy = date.today()
            edad = (
                hoy.year
                - nacimiento.year
                - ((hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))
            )
        except Exception:
            edad = 23

    return {
        "peso": round(float(peso), 1),
        "altura": float(altura),
        "edad": int(edad),
        "objetivo": "Ganar masa + triatlón",
        "superavit": 300,
        "target_swim_min": 30,
        "target_bike_min": 80,
        "target_run_min": 42,
    }


def cargar_perfil():
    columnas = [
        "peso",
        "altura",
        "edad",
        "objetivo",
        "superavit",
        "target_swim_min",
        "target_bike_min",
        "target_run_min",
    ]

    user_id = get_current_user_id()

    res = (
        _client()
        .table("profiles")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )

    if res.data:
        perfil = res.data[0]
        return pd.Series({col: perfil.get(col) for col in columnas})

    perfil_garmin = st.session_state.get("perfil_garmin", {})
    perfil_base = crear_perfil_desde_garmin(perfil_garmin)

    data = {
        "user_id": user_id,
        **perfil_base,
    }

    (_client().table("profiles").upsert(data, on_conflict="user_id").execute())

    return pd.Series(perfil_base)


def guardar_perfil(peso, altura, edad, superavit, swim, bike, run):
    user_id = get_current_user_id()

    data = {
        "user_id": user_id,
        "peso": float(peso),
        "altura": float(altura),
        "edad": int(edad),
        "objetivo": "Ganar masa + triatlón",
        "superavit": int(superavit),
        "target_swim_min": float(swim),
        "target_bike_min": float(bike),
        "target_run_min": float(run),
    }

    (_client().table("profiles").upsert(data, on_conflict="user_id").execute())


# ============================================================
# PESO
# ============================================================


def cargar_peso():
    columnas = ["fecha", "peso"]

    user_id = get_current_user_id()

    res = (
        _client()
        .table("weight_logs")
        .select(",".join(columnas))
        .eq("user_id", user_id)
        .order("fecha")
        .execute()
    )

    df = _to_df(res.data, columnas)

    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce").dt.date

    return df


def guardar_peso(fecha, peso):
    user_id = get_current_user_id()

    data = {
        "user_id": user_id,
        "fecha": _fecha_str(fecha),
        "peso": float(peso),
    }

    (_client().table("weight_logs").upsert(data, on_conflict="user_id,fecha").execute())


# ============================================================
# FAVORITOS
# ============================================================


def cargar_favoritos():
    columnas = ["nombre_favorito", "comida", "alimento", "gramos"]

    user_id = get_current_user_id()

    res = (
        _client()
        .table("favorite_meals")
        .select(",".join(columnas))
        .eq("user_id", user_id)
        .order("nombre_favorito")
        .execute()
    )

    return _to_df(res.data, columnas)


def guardar_favorito(nombre_favorito, comida, alimento, gramos):
    user_id = get_current_user_id()

    data = {
        "user_id": user_id,
        "nombre_favorito": nombre_favorito,
        "comida": comida,
        "alimento": alimento,
        "gramos": float(gramos or 0),
    }

    _client().table("favorite_meals").insert(data).execute()


def registrar_favorito(nombre_favorito, fecha):
    favoritos = cargar_favoritos()
    alimentos = cargar_alimentos()

    fav = favoritos[favoritos["nombre_favorito"] == nombre_favorito]

    if fav.empty:
        return False

    for _, item in fav.iterrows():
        alimento = item["alimento"]
        gramos = float(item["gramos"])
        comida = item["comida"]

        fila = alimentos[alimentos["nombre"] == alimento]

        if fila.empty:
            continue

        fila = fila.iloc[0]
        factor = gramos / 100

        kcal = round(float(fila["kcal_100g"]) * factor, 1)
        proteina = round(float(fila["proteina_100g"]) * factor, 1)
        carbos = round(float(fila["carbos_100g"]) * factor, 1)
        grasas = round(float(fila["grasas_100g"]) * factor, 1)

        guardar_comida(
            fecha,
            comida,
            alimento,
            gramos,
            kcal,
            proteina,
            carbos,
            grasas,
        )

    return True

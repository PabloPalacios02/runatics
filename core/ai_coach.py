import google.generativeai as genai
from config.settings import cargar_secrets

secrets = cargar_secrets()

def inicializar_gemini():
    api_key = secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    return genai.GenerativeModel("gemini-2.5-flash")


def construir_contexto_ia(df, salud, perfil):
    contexto = f"""
Eres un entrenador de triatlón, nutricionista deportivo y preparador físico.

DATOS DEL USUARIO

Edad: {perfil['edad']}
Peso: {perfil['peso']} kg
Altura: {perfil['altura']} cm

Objetivos:
- Ganar masa muscular
- Preparar triatlón olímpico
- Fecha objetivo: 27 septiembre 2026

Últimas actividades:
{df.tail(20).to_string()}

Últimos datos de salud:
{salud.tail(14).to_string()}

Debes responder de forma práctica,
explicando claramente las decisiones.
"""
    return contexto


def preguntar_coach_ia(pregunta, df, salud, perfil):
    modelo = inicializar_gemini()

    contexto = construir_contexto_ia(df, salud, perfil)

    prompt = f"""
{contexto}

PREGUNTA DEL USUARIO:

{pregunta}
"""

    respuesta = modelo.generate_content(prompt)

    return respuesta.text

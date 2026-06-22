# GarminDashboard refactorizado

Ejecutar:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Crea un `secrets.toml` real a partir de `secrets.toml.example`. No he incluido tu `secrets.toml` original para no compartir claves privadas.

## Estructura

- `app.py`: interfaz principal Streamlit.
- `config/settings.py`: constantes y carga de secretos.
- `services/garmin_service.py`: conexión y normalización Garmin.
- `services/strava_service.py`: conexión y normalización Strava.
- `core/activity_merge.py`: fusión y eliminación de duplicados.
- `core/training_metrics.py`: recomendaciones, predicción, planificación y recuperación.
- `core/nutrition_metrics.py`: sugerencias nutricionales.
- `core/ai_coach.py`: coach IA con Gemini.
- `data_store/storage.py`: lectura/escritura CSV por usuario.

import pandas as pd

def sugerir_comidas_para_macros(
    alimentos, kcal_faltan, proteina_falta, carbos_faltan, grasas_faltan
):
    if alimentos.empty:
        return pd.DataFrame()

    alimentos = alimentos.copy()
    sugerencias = []

    # Priorizar alimentos altos en proteína si falta proteína
    alimentos["ratio_proteina"] = alimentos["proteina_100g"] / alimentos[
        "kcal_100g"
    ].replace(0, 1)

    candidatos_proteina = alimentos.sort_values("ratio_proteina", ascending=False).head(
        5
    )
    candidatos_carbo = alimentos.sort_values("carbos_100g", ascending=False).head(5)
    candidatos_grasa = alimentos.sort_values("grasas_100g", ascending=False).head(5)

    def añadir_sugerencia(nombre, gramos):
        fila = alimentos[alimentos["nombre"] == nombre].iloc[0]
        factor = gramos / 100

        sugerencias.append(
            {
                "Alimento": nombre,
                "Gramos": round(gramos),
                "Kcal": round(fila["kcal_100g"] * factor),
                "Proteína": round(fila["proteina_100g"] * factor, 1),
                "Carbos": round(fila["carbos_100g"] * factor, 1),
                "Grasas": round(fila["grasas_100g"] * factor, 1),
            }
        )

    if proteina_falta > 25 and not candidatos_proteina.empty:
        añadir_sugerencia(
            candidatos_proteina.iloc[0]["nombre"],
            min(
                max(
                    proteina_falta
                    / max(candidatos_proteina.iloc[0]["proteina_100g"], 1)
                    * 100,
                    80,
                ),
                250,
            ),
        )

    if carbos_faltan > 40 and not candidatos_carbo.empty:
        añadir_sugerencia(
            candidatos_carbo.iloc[0]["nombre"],
            min(
                max(
                    carbos_faltan
                    / max(candidatos_carbo.iloc[0]["carbos_100g"], 1)
                    * 100,
                    60,
                ),
                200,
            ),
        )

    if grasas_faltan > 15 and not candidatos_grasa.empty:
        añadir_sugerencia(
            candidatos_grasa.iloc[0]["nombre"],
            min(
                max(
                    grasas_faltan
                    / max(candidatos_grasa.iloc[0]["grasas_100g"], 1)
                    * 100,
                    20,
                ),
                80,
            ),
        )

    return pd.DataFrame(sugerencias)


def generar_cena_sugerida(
    alimentos, kcal_faltan, proteina_falta, carbos_faltan, grasas_faltan
):
    if alimentos.empty:
        return pd.DataFrame()

    alimentos = alimentos.copy()

    # Evitar alimentos sin datos
    alimentos = alimentos[
        (alimentos["kcal_100g"] > 0)
        | (alimentos["proteina_100g"] > 0)
        | (alimentos["carbos_100g"] > 0)
        | (alimentos["grasas_100g"] > 0)
    ]

    if alimentos.empty:
        return pd.DataFrame()

    alimentos["ratio_proteina"] = alimentos["proteina_100g"] / alimentos[
        "kcal_100g"
    ].replace(0, 1)

    sugerencia = []

    def add_food(fila, gramos):
        factor = gramos / 100
        sugerencia.append(
            {
                "Alimento": fila["nombre"],
                "Gramos": round(gramos),
                "Kcal": round(fila["kcal_100g"] * factor),
                "Proteína": round(fila["proteina_100g"] * factor, 1),
                "Carbos": round(fila["carbos_100g"] * factor, 1),
                "Grasas": round(fila["grasas_100g"] * factor, 1),
            }
        )

    # 1. Fuente principal de proteína
    if proteina_falta > 20:
        prot = alimentos.sort_values("ratio_proteina", ascending=False).iloc[0]
        gramos = min(
            max((proteina_falta * 0.7) / max(prot["proteina_100g"], 1) * 100, 100), 250
        )
        add_food(prot, gramos)

    # 2. Fuente principal de carbohidratos
    if carbos_faltan > 40:
        carb = alimentos.sort_values("carbos_100g", ascending=False).iloc[0]
        gramos = min(
            max((carbos_faltan * 0.6) / max(carb["carbos_100g"], 1) * 100, 60), 250
        )
        add_food(carb, gramos)

    # 3. Fuente de grasa si falta
    if grasas_faltan > 15:
        grasa = alimentos.sort_values("grasas_100g", ascending=False).iloc[0]
        gramos = min(
            max((grasas_faltan * 0.5) / max(grasa["grasas_100g"], 1) * 100, 15), 80
        )
        add_food(grasa, gramos)

    resultado = pd.DataFrame(sugerencia)

    if resultado.empty:
        return resultado

    return resultado


def generar_menu_restante(
    alimentos, kcal_faltan, proteina_falta, carbos_faltan, grasas_faltan
):
    if alimentos.empty:
        return pd.DataFrame()

    alimentos = alimentos.copy()
    alimentos = alimentos[
        (alimentos["kcal_100g"] > 0)
        | (alimentos["proteina_100g"] > 0)
        | (alimentos["carbos_100g"] > 0)
        | (alimentos["grasas_100g"] > 0)
    ]

    if alimentos.empty:
        return pd.DataFrame()

    alimentos["ratio_proteina"] = alimentos["proteina_100g"] / alimentos[
        "kcal_100g"
    ].replace(0, 1)

    menu = []

    def añadir(comida, fila, gramos):
        factor = gramos / 100
        menu.append(
            {
                "Comida": comida,
                "Alimento": fila["nombre"],
                "Gramos": round(gramos),
                "Kcal": round(fila["kcal_100g"] * factor),
                "Proteína": round(fila["proteina_100g"] * factor, 1),
                "Carbos": round(fila["carbos_100g"] * factor, 1),
                "Grasas": round(fila["grasas_100g"] * factor, 1),
            }
        )

    prot = alimentos.sort_values("ratio_proteina", ascending=False).iloc[0]
    carb = alimentos.sort_values("carbos_100g", ascending=False).iloc[0]
    grasa = alimentos.sort_values("grasas_100g", ascending=False).iloc[0]

    if proteina_falta > 30:
        añadir(
            "Comida/Cena",
            prot,
            min(
                max(proteina_falta * 0.55 / max(prot["proteina_100g"], 1) * 100, 100),
                250,
            ),
        )

    if carbos_faltan > 50:
        añadir(
            "Comida/Cena",
            carb,
            min(max(carbos_faltan * 0.55 / max(carb["carbos_100g"], 1) * 100, 80), 250),
        )

    if grasas_faltan > 15:
        añadir(
            "Snack/Merienda",
            grasa,
            min(max(grasas_faltan * 0.45 / max(grasa["grasas_100g"], 1) * 100, 15), 80),
        )

    if kcal_faltan > 500 and proteina_falta > 15:
        añadir("Snack/Merienda", prot, 100)

    return pd.DataFrame(menu)

from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[2]

CARPETA_DATASET = BASE / "Output" / "dataset"

RUTA_CSV = CARPETA_DATASET / "ventas_analizadas.csv"

def generar_dataset(ventas_completas, df_resultados_ia):

    # Crear carpeta de salida si no existe
    CARPETA_DATASET.mkdir(parents=True, exist_ok=True)

    columnas_ia = [
        "id_venta",
        "casos_uso",
        "recomendaciones_operativas",
        "limitaciones_tecnicas",
        "score_compatibilidad",
        "complejidad",
        "justificacion_score"
    ]

    resultados_ia = df_resultados_ia[[columna for columna in columnas_ia if columna in df_resultados_ia.columns]].copy()

    dataset = pd.merge(
        ventas_completas,
        resultados_ia,
        on="id_venta",
        how="left",
        validate="one_to_one"
    )

    # Identificar ventas con y sin análisis de IA
    dataset["estado_analisis_ia"] = dataset["score_compatibilidad"].apply(
        lambda score: "Analizado" if pd.notna(score) else "Pendiente"
    )

    # Convertir listas de IA en texto
    columnas_lista = [
        "casos_uso",
        "recomendaciones_operativas",
        "limitaciones_tecnicas"
    ]

    for columna in columnas_lista:

        if columna in dataset.columns:

            dataset[columna] = dataset[columna].apply(
                lambda elementos: "; ".join(map(str, elementos))
                if isinstance(elementos, list)
                else elementos
            )

    dataset["fecha_venta"] = pd.to_datetime(
        dataset["fecha_venta"],
        dayfirst=True,
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")
    
    # Exportar CSV
    dataset.to_csv(
        RUTA_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Dataset generado correctamente: {RUTA_CSV}")

    return dataset

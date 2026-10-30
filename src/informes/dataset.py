from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[2]

CARPETA_DATASET = BASE / "Output" / "dataset"

RUTA_CSV = CARPETA_DATASET / "ventas_analizadas.csv"
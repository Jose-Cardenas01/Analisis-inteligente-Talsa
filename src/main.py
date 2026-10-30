import pandas as pd
from pathlib import Path
import re
import unicodedata

BASE = Path(r"C:\Users\JOSE CARDENAS\OneDrive\Escritorio\Talsa2.0")

clientes_ventas = pd.read_json(
    BASE / "clientes_ventas.json"
)

with open(
    BASE / "catalogo_equipos_raw.txt",
    "r",
    encoding="utf-8"
) as archivo:
    txt_catalogo = archivo.read()

catalogo_equipos_raw = pd.DataFrame({
    "txt": txt_catalogo.splitlines()
})

with open(
    BASE / "perfil_cliente_contexto.txt",
    "r",
    encoding="utf-8"
) as archivo:
    txt_cliente = archivo.read()

perfil_cliente = pd.DataFrame({
    "txt": txt_cliente.splitlines()
})

columnas_texto = [
    "empresa",
    "industria",
    "equipo_comprado",
    "ubicacion"
]

for columna in columnas_texto:
    clientes_ventas[columna] = (
        clientes_ventas[columna]
        .astype("string")
        .str.strip()
    )

clientes_ventas["fecha_venta"] = pd.to_datetime(
    clientes_ventas["fecha_venta"],
    errors="coerce"
)

clientes_ventas["monto_usd"] = pd.to_numeric(
    clientes_ventas["monto_usd"]
        .astype("string")
        .str.replace(r"[$,\s]", "", regex=True),
    errors="coerce"
)
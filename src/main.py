import pandas as pd
from pathlib import Path
import re
import unicodedata
import os
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types

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

def normalizar_codigo(valor):

    return re.sub(r"[^A-Z0-9]", "", str(valor).upper())


clientes_ventas["codigo_equipo"] = (
    clientes_ventas["equipo_comprado"]
    .apply(normalizar_codigo)
)

bloques_catalogo = re.split(
    r"(?=^(?:PASTEURIZADOR|CALDERA|LIOFILIZADOR)\b)",
    txt_catalogo.strip(),
    flags=re.IGNORECASE | re.MULTILINE
)

equipos = []

for bloque in bloques_catalogo:

    coincidencia = re.search(r"\b(PX[\s-]?3000|CV[\s-]?150|LF[\s-]?50)\b", bloque, flags=re.IGNORECASE)

    if coincidencia:

        codigo = normalizar_codigo(coincidencia.group())

        equipos.append({
            "codigo_equipo": codigo,
            "ficha_tecnica": bloque.strip()
        })


catalogo_equipos = pd.DataFrame(equipos)

ventas_con_equipos = clientes_ventas.merge(
    catalogo_equipos,
    on="codigo_equipo",
    how="left",
    validate="many_to_one"
)

bloques_perfil = re.split(
    r"\n\s*\n",
    txt_cliente.strip()
)

perfiles = []

for bloque in bloques_perfil:

    texto = bloque.strip()

    texto_normalizado = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8").lower()

    if "lacteos" in texto_normalizado:
        empresa = "Lácteos"

    elif "hilanderia" in texto_normalizado:
        empresa = "Hilandería"

    elif "biofarma" in texto_normalizado:
        empresa = "Biofarma"

    else:
        continue

    perfiles.append({
        "empresa": empresa,
        "perfil_cliente": texto
    })


perfiles_clientes = pd.DataFrame(perfiles)

ventas_completas = ventas_con_equipos.merge(
    perfiles_clientes,
    on="empresa",
    how="left",
    validate="many_to_one"
)

print("Total de ventas:", len(ventas_completas))

print(
    "Ventas sin ficha técnica:",
    ventas_completas["ficha_tecnica"].isna().sum()
)

print(
    "Ventas sin perfil de cliente:",
    ventas_completas["perfil_cliente"].isna().sum()
)

print(ventas_completas[
    [
        "id_venta",
        "empresa",
        "fecha_venta",
        "monto_usd",
        "equipo_comprado",
        "codigo_equipo",
    ]
])

load_dotenv()

api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("No se encontró la API Key de Gemini")

# Crear el cliente de Gemini
client = genai.Client(api_key=api_key)

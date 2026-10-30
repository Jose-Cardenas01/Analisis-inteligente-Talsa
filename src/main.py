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

# catalogo_equipos_raw = pd.DataFrame({
#     "txt": txt_catalogo.splitlines()
# })

with open(
    BASE / "perfil_cliente_contexto.txt",
    "r",
    encoding="utf-8"
) as archivo:
    txt_cliente = archivo.read()

# perfil_cliente = pd.DataFrame({
#     "txt": txt_cliente.splitlines()
# })

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

def extraer_codigo_equipo(valor):

    coincidencia = re.search(
        r"\b(PX[\s-]?3000|CV[\s-]?150|LF[\s-]?50)\b",
        str(valor),
        flags=re.IGNORECASE
    )

    if coincidencia:
        return normalizar_codigo(coincidencia.group())

    return None

clientes_ventas["codigo_equipo"] = (
    clientes_ventas["equipo_comprado"]
    .apply(extraer_codigo_equipo)
)

bloques_catalogo = re.split(
    r"(?=^(?:[ \t]*#+[ \t]*PASTEURIZADOR|"
    r"[ \t]*-+[ \t]*\n[ \t]*CALDERA|"
    r"[ \t]*-+[ \t]*LIOFILIZADOR)\b)",
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
        empresa = "Lácteos del Valle S.A.S."

    elif "hilanderia" in texto_normalizado:
        empresa = "Hilandería Andina S.A."

    elif "biofarma" in texto_normalizado:
        empresa = "Laboratorios Biofarma Ltda."

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

# print(ventas_completas[
#     [
#         "empresa",
#         "codigo_equipo",
#         "ficha_tecnica"
#     ]
# ].to_string(index=False))

# print(
#     ventas_completas[
#         ["codigo_equipo", "ficha_tecnica"]
#     ].notna()
# )

# print(ventas_completas[
#     [
#         "id_venta",
#         "empresa",
#         "fecha_venta",
#         "monto_usd",
#         "equipo_comprado",
#         "codigo_equipo",
#         "perfil_cliente"
#     ]
# ])

load_dotenv()

api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("No se encontró la API Key de Gemini")

client = genai.Client(api_key=api_key)

def validar_resultado(resultado):

    campos_obligatorios = [
        "casos_uso",
        "recomendaciones_operativas",
        "limitaciones_tecnicas",
        "score_compatibilidad",
        "complejidad"
    ]

    # Comprobar que todos los campos existan
    for campo in campos_obligatorios:

        if campo not in resultado:
            raise ValueError(f"Falta el campo: {campo}")

    # Comprobar que las tres primeras propiedades sean listas
    for campo in [
        "casos_uso",
        "recomendaciones_operativas",
        "limitaciones_tecnicas"
    ]:

        if not isinstance(resultado[campo], list):
            raise ValueError(f"{campo} debe ser una lista")

    # Comprobar que el score sea numérico y esté entre 0 y 100
    score = resultado["score_compatibilidad"]

    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise ValueError("El score debe ser numérico")

    if not 0 <= score <= 100:
        raise ValueError("El score debe estar entre 0 y 100")

    # Comprobar la complejidad
    if resultado["complejidad"] not in ["Alto", "Medio", "Bajo"]:
        raise ValueError("La complejidad debe ser Alto, Medio o Bajo")

    return True

resultados_ia = []

for indice, venta in ventas_completas.iterrows():

    ficha_tecnica = venta["ficha_tecnica"]
    perfil_cliente = venta["perfil_cliente"]

    if pd.isna(ficha_tecnica) or pd.isna(perfil_cliente):
        continue

    prompt = f"""
    Analiza la compatibilidad entre el equipo y el cliente.

    FICHA TÉCNICA:
    {ficha_tecnica}

    PERFIL DEL CLIENTE:
    {perfil_cliente}

    Devuelve un JSON con las siguientes propiedades:

    - casos_uso: lista de casos de uso.
    - recomendaciones_operativas: lista de recomendaciones.
    - limitaciones_tecnicas: lista de limitaciones.
    - score_compatibilidad: número entre 0 y 100.
    - complejidad: Alto, Medio o Bajo.

    CRITERIOS PARA EL SCORE DE COMPATIBILIDAD:

    Evalúa la compatibilidad considerando:

    1. Correspondencia entre las capacidades del equipo
    y las necesidades productivas del cliente.

    2. Compatibilidad de las condiciones operativas:
    energía, temperatura, presión, agua y servicios requeridos.

    3. Infraestructura disponible en las instalaciones del cliente.

    4. Requisitos de calidad, seguridad y regulación aplicables.

    Asigna un score de 0 a 100 según el nivel de compatibilidad.

    Justifica brevemente el score asignado.

    La complejidad debe representar el nivel de dificultad
    de implementación y adaptación del equipo al contexto
    del cliente.

    IMPORTANTE:
    El catálogo contiene información técnica preliminar que no ha sido
    validada completamente por el fabricante. No presentes sus datos
    como especificaciones certificadas. Señala los datos que requieren
    confirmación.
    """

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )

        resultado = json.loads(response.text)

        validar_resultado(resultado)

        resultados_ia.append({
            "id_venta": venta["id_venta"],
            "empresa": venta["empresa"],
            "equipo_comprado": venta["equipo_comprado"],
            **resultado
        })

    except (json.JSONDecodeError, TypeError, ValueError) as error:

        print(f"Error procesando la venta {venta['id_venta']}: {error}")

    except Exception as error:

        print(f"Error de Gemini en la venta {venta['id_venta']}: {error}")


df_resultados_ia = pd.DataFrame(resultados_ia)

columnas = [
    "id_venta",
    "empresa",
    "score_compatibilidad",
    "complejidad",
    "justificacion_score"
]

print(df_resultados_ia[columnas].to_string(index=False))

print("\nCampos vacíos:")
print(df_resultados_ia.isnull().sum())

# print(df_resultados_ia.to_string(index=False))
# print("Análisis generados:", len(df_resultados_ia))
# print("Ventas originales:", len(ventas_completas))

# print(clientes_ventas["empresa"].unique())
# print(perfiles_clientes["empresa"].unique())
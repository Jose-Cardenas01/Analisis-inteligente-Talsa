import pandas as pd
import os
import json

from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

from src.IA.prompts import construir_prompt
from src.IA.validaciones import validar_resultado

BASE = Path(r"C:\Users\JOSE CARDENAS\OneDrive\Escritorio\Talsa2.0")

def analizar_ventas(ventas_completas):

    load_dotenv(dotenv_path=BASE / ".env")

    api_key = os.getenv("API_KEY")

    if not api_key:
        raise ValueError("No se encontró la API Key de Gemini")

    client = genai.Client(api_key=api_key)

    resultados_ia = []

    # Recorrer las ventas completas
    for indice, venta in ventas_completas.iterrows():

        ficha_tecnica = venta["ficha_tecnica"]
        perfil_cliente = venta["perfil_cliente"]

        if pd.isna(ficha_tecnica) or pd.isna(perfil_cliente):
            continue

        prompt = construir_prompt(ficha_tecnica, perfil_cliente)

        try:

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
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

            print(f"Error procesando la venta " f"{venta['id_venta']}: {error}")

        except Exception as error:

            print(
                f"Error de Gemini en la venta "
                f"{venta['id_venta']}: {error}"
            )

    df_resultados_ia = pd.DataFrame(resultados_ia)

    return df_resultados_ia
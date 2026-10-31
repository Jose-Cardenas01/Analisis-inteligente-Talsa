import pandas as pd
from pathlib import Path

BASE = Path(r"C:\Users\JOSE CARDENAS\OneDrive\Escritorio\Talsa2.0")


def cargar_datos():
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
        
    return clientes_ventas, txt_catalogo, txt_cliente
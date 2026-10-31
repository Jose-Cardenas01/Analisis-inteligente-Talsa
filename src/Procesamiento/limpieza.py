import pandas as pd


def limpiar_datos(clientes_ventas):
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
    return clientes_ventas
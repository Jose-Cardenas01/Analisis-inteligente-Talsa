
from src.Procesamiento.cargar_datos import cargar_datos
from src.Procesamiento.limpieza import limpiar_datos
from src.Procesamiento.relaciones import relacionar_datos

from src.IA.gemini import analizar_ventas


def main():

    clientes_ventas, txt_catalogo, txt_cliente = cargar_datos()

    clientes_ventas = limpiar_datos(clientes_ventas)

    ventas_completas = relacionar_datos(clientes_ventas, txt_catalogo, txt_cliente)

    df_resultados_ia = analizar_ventas(ventas_completas)

    columnas = [
        "id_venta",
        "empresa",
        "score_compatibilidad",
        "complejidad",
        "justificacion_score"
    ]

    if not df_resultados_ia.empty:

        print(
            df_resultados_ia[columnas].to_string(index=False)
        )

        print("\nCampos vacíos:")
        print(df_resultados_ia.isnull().sum())

    else:
        print("No se generaron resultados de IA.")


if __name__ == "__main__":
    main()

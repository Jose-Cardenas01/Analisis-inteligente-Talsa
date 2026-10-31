
from src.Procesamiento.cargar_datos import cargar_datos
from src.Procesamiento.limpieza import limpiar_datos
from src.Procesamiento.relaciones import relacionar_datos
from src.informes.pdf import generar_informes
from src.informes.dataset import generar_dataset

from src.IA.gemini import analizar_ventas


# 1. Cargar los archivos
clientes_ventas, txt_catalogo, txt_cliente = cargar_datos()

# 2. Limpiar los datos
clientes_ventas = limpiar_datos(clientes_ventas)

# 3. Relacionar ventas, equipos y perfiles
ventas_completas = relacionar_datos(
    clientes_ventas,
    txt_catalogo,
    txt_cliente
)

# 4. Analizar las ventas con Gemini
df_resultados_ia = analizar_ventas(ventas_completas)

# 5. Generar dataset para Looker Studio
dataset = generar_dataset(ventas_completas, df_resultados_ia)

# 5. Generar los informes PDF
generar_informes(ventas_completas, df_resultados_ia)

# 6. Mostrar resultados
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

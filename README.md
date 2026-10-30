Talsa – Pipeline de Análisis Inteligente de Ventas con IA

1. Descripción del proyecto

Este proyecto implementa un pipeline de procesamiento y análisis inteligente de ventas para Talsa, utilizando Python, Pandas y Google Gemini.

Su objetivo es integrar información comercial, especificaciones técnicas de equipos industriales y perfiles de clientes para generar recomendaciones personalizadas mediante inteligencia artificial.

El sistema procesa automáticamente los archivos de entrada, relaciona la información disponible, analiza la compatibilidad entre los equipos adquiridos y las necesidades de cada cliente, y genera informes individuales en PDF junto con un dataset preparado para su visualización en Looker Studio.

Resultados generados

- Tres informes PDF, uno por cada venta analizada.
- Un archivo CSV consolidado con la información comercial y los resultados del análisis de IA.
- Un dashboard interactivo en Looker Studio para visualizar los indicadores y explorar los resultados.

2. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python | Lenguaje principal del proyecto. |
| Pandas | Carga, limpieza, transformación y relación de datos. |
| Google Gemini API | Análisis inteligente de compatibilidad entre equipos y clientes. |
| Google GenAI SDK | Integración con el modelo Gemini. |
| python-dotenv | Gestión de variables de entorno. |
| ReportLab | Generación de informes PDF. |
| Looker Studio | Visualización y análisis de los resultados. |

3. Estructura del proyecto

Talsa2.0/
│
├── src/
│   │
│   ├── Procesamiento/
│   │   ├── cargar_datos.py
│   │   ├── limpieza.py
│   │   └── relaciones.py
│   │
│   ├── IA/
│   │   ├── prompts.py
│   │   ├── validaciones.py
│   │   └── gemini.py
│   │
│   ├── informes/
│   │   ├── pdf.py
│   │   └── dataset.py
│   │
│   └── assets/
│       └── talsa-logo.png
│
├── Output/
│   ├── dataset/
│   │   └── ventas_analizadas.csv
│   │
│   └── PDF/
│       ├── informe_V-2026-0101.pdf
│       ├── informe_V-2026-0102.pdf
│       └── informe_V-2026-0103.pdf
│
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── README.md

Cada módulo tiene una responsabilidad específica:

- `Procesamiento`: carga, limpieza, normalización y relación de los datos.
- `IA`: construcción del prompt, comunicación con Gemini y validación de las respuestas.
- `informes`: generación de documentos PDF y construcción del dataset para Looker Studio.
- `assets`: recursos gráficos utilizados en los informes.
- `salida`: almacenamiento de los archivos generados.
- `main.py`: punto de entrada que coordina la ejecución de todo el proceso.

4. Requisitos e instalación

Requisitos previos

- Python instalado.
- Conexión a Internet para utilizar Google Gemini API.
- Una API Key de Google AI Studio.

Instalación de dependencias

Desde la terminal, ubicada en la carpeta raíz del proyecto, ejecutar:

pip install -r requirements.txt

Configuración de la API Key

Crear un archivo `.env` en la raíz del proyecto con la siguiente variable:

API_KEY=TU_API_KEY_DE_GEMINI

Reemplazar `TU_API_KEY_DE_GEMINI` por la clave correspondiente.

La API Key se carga mediante `python-dotenv`, evitando incluir credenciales directamente en el código fuente.

**Importante:** el archivo `.env` no debe subirse al repositorio. Debe estar incluido en `.gitignore`.

5. Ejecución del programa

El proyecto está organizado para ejecutar todo el procesamiento mediante un único comando.

Desde la terminal, ubicarse en la carpeta raíz del proyecto y ejecutar:

python main.py

El main realiza automáticamente las siguientes etapas:

1. Carga de los archivos de ventas, catálogo de equipos y perfiles de clientes.
2. Limpieza y normalización de la información.
3. Identificación y relación de ventas, equipos y clientes.
4. Envío de la información relacionada a Google Gemini.
5. Validación y almacenamiento de los resultados del análisis.
6. Generación de un informe PDF individual por cada venta.
7. Consolidación de la información comercial y los resultados de IA en un archivo CSV.

Los documentos generados se almacenan en la carpeta `Output/`.

6. Decisiones técnicas

6.1. Cruce de información sin claves comunes

Uno de los principales desafíos fue relacionar tres fuentes de información que no compartían una clave primaria o un identificador común entre ellas.

Las fuentes utilizadas fueron:

- `clientes_ventas.json`: contiene los registros comerciales de las ventas.
- `catalogo_equipos_raw.txt`: contiene las especificaciones técnicas de los equipos.
- `perfil_cliente_contexto.txt`: contiene información sobre las actividades, necesidades y condiciones operativas de los clientes.

Para solucionar este problema se implementó una estrategia de identificación y normalización basada en atributos existentes en los documentos.

Relación entre ventas y equipos:

Se utilizó el código del equipo como criterio de identificación. Mediante expresiones regulares se extraen códigos como `PX-3000`, `CV-150` y `LF-50`, eliminando caracteres especiales y unificando su representación.

De esta manera, diferentes formatos de un mismo código pueden reconocerse como un único identificador.

Relación entre ventas y perfiles de clientes:

Se utilizó el nombre de la empresa como criterio de correspondencia, considerando que los registros comerciales y los perfiles de contexto identifican a los clientes mediante su razón social.

Integración final:

Una vez identificadas las correspondencias, se utilizaron operaciones `merge` de Pandas para integrar la información.

Se aplicaron validaciones de cardinalidad para comprobar que las relaciones cumplieran las condiciones esperadas y evitar duplicaciones inesperadas.

Esta estrategia permite relacionar información que originalmente se encuentra distribuida en diferentes archivos, sin necesidad de modificar las fuentes originales ni disponer de claves compartidas.

6.2. Diseño del prompt para Gemini

Se utilizó Google Gemini para evaluar la compatibilidad entre las características técnicas de los equipos adquiridos y las necesidades operativas de los clientes.

El prompt proporciona dos elementos principales:

- La ficha técnica del equipo adquirido.
- El perfil contextual del cliente.

A partir de esta información, se solicita al modelo generar un análisis estructurado que incluya:

- `casos_uso`: posibles aplicaciones del equipo en las operaciones del cliente.
- `recomendaciones_operativas`: recomendaciones para su implementación y operación.
- `limitaciones_tecnicas`: restricciones o condiciones que pueden afectar su funcionamiento.
- `score_compatibilidad`: puntuación de compatibilidad entre 0 y 100.
- `complejidad`: clasificación en Alto, Medio o Bajo.
- `justificacion_score`: explicación de la puntuación asignada.

Se solicitó una respuesta en formato JSON para facilitar su procesamiento automático desde Python.

Además, se implementaron validaciones para comprobar la estructura de la respuesta, la presencia de los campos requeridos, el rango del score y los valores permitidos para la complejidad.

Esto permite detectar respuestas incompletas o inválidas antes de incorporarlas al dataset y generar los informes.

6.3. Generación de informes PDF

Se utilizó ReportLab para generar un documento individual por cada venta.

Cada informe contiene:

- Información comercial y de facturación.
- Identificación y especificaciones técnicas del equipo.
- Resultados del análisis de inteligencia artificial.
- Casos de uso, recomendaciones y limitaciones.
- Score de compatibilidad y nivel de complejidad.

Se aplicó una identidad visual basada en la paleta de colores de Talsa:

| Color | Código hexadecimal | Uso |
|---|---|---|
| Rojo Talsa | `#DC182A` | Títulos y encabezados de tablas. |
| Negro | `#000000` | Texto principal y logotipo. |
| Gris | `#808080` | Información secundaria. |
| Gris claro | `#F4F4F4` | Fondos y filas alternas. |
| Blanco | `#FFFFFF` | Fondo y texto de encabezados. |
| Rojo oscuro | `#B01220` | Elementos de énfasis. |

6.4. Generación del dataset para Looker Studio

Se consolidaron los datos comerciales y los resultados del análisis de Gemini mediante el identificador de venta.

El resultado es un dataset que contiene información como:

- Identificador de venta y cliente.
- Empresa e industria.
- Equipo adquirido y código del equipo.
- Fecha de venta y monto.
- Ubicación.
- Ficha técnica y perfil del cliente.
- Casos de uso y recomendaciones.
- Limitaciones técnicas.
- Score de compatibilidad.
- Complejidad y justificación del análisis.
- Estado del análisis de IA.

El archivo se exporta en formato CSV con codificación UTF-8 con BOM para facilitar su lectura en herramientas de visualización.

También se normaliza la fecha de venta para facilitar su reconocimiento como campo de tipo fecha.

7. Dashboard en Looker Studio

El archivo CSV generado se utiliza como fuente de datos para construir un dashboard interactivo en Looker Studio.

El dashboard incluye los siguientes componentes:

Indicadores KPI

- Total de ventas en USD.
- Compatibilidad promedio de los equipos analizados.

Gráficos

- Ventas en USD por industria.
- Distribución de complejidad técnica por tipo de equipo.

Filtros dinámicos

- Industria.
- Tipo de equipo.
- Intervalo de fechas.

Estos componentes permiten explorar los resultados desde diferentes perspectivas y analizar la relación entre las ventas, los equipos adquiridos y su compatibilidad con las necesidades de los clientes.

8. Limitaciones identificadas

Durante el desarrollo se identificaron las siguientes limitaciones:

- **Calidad de las fuentes:** la información técnica disponible es preliminar y algunos datos requieren validación con los fabricantes.
- **Cruce de información:** la correspondencia por códigos de equipos y nombres de empresas depende de la consistencia de los datos originales. Diferencias importantes en los nombres o códigos pueden impedir una relación correcta.
- **Dependencia de la API:** el análisis requiere conexión a Internet y disponibilidad de Google Gemini. Pueden presentarse errores temporales de disponibilidad o límites de cuota.
- **Resultados de IA:** los scores y las recomendaciones son orientativos y no representan una certificación técnica ni sustituyen una evaluación realizada por especialistas.
- **Contexto limitado:** la calidad del análisis depende de la cantidad, precisión y actualidad de la información proporcionada al modelo.
- **Validación técnica:** las recomendaciones generadas deben revisarse antes de utilizarlas para tomar decisiones operativas o comerciales.

## 9. Mejoras futuras

Con más tiempo y recursos, se podrían implementar las siguientes mejoras:

1. Incorporar identificadores únicos y estandarizados para clientes y equipos, reduciendo la dependencia de coincidencias textuales.
2. Implementar pruebas automatizadas para validar la limpieza, las relaciones y la generación de resultados.
3. Incorporar mecanismos de reintentos para mejorar la disponibilidad del análisis mediante Gemini.
4. Implementar un registro de ejecuciones para conservar el historial de análisis y facilitar su seguimiento.
5. Validar las especificaciones técnicas mediante fuentes oficiales de los fabricantes.
6. Incorporar nuevos indicadores al dashboard para analizar tendencias y comparar resultados con un mayor volumen de ventas.

10. Consideraciones finales

El proyecto demuestra cómo integrar técnicas de procesamiento de datos e inteligencia artificial para transformar información comercial y técnica dispersa en resultados estructurados y útiles para el análisis empresarial.

La solución automatiza el procesamiento de las ventas, relaciona información sin claves comunes, utiliza un modelo de lenguaje para generar análisis de compatibilidad y produce informes individuales y un dataset listo para su visualización en Looker Studio.

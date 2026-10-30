
import re
import html
from pathlib import Path
from reportlab.lib.utils import ImageReader

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)

# Paleta corporativa Talsa
COLOR_TALSA = colors.HexColor("#DC182A")       # Rojo primario
COLOR_NEGRO = colors.HexColor("#000000")       # Texto y logotipo
COLOR_GRIS = colors.HexColor("#808080")        # Subtítulos y pie de página
COLOR_GRIS_CLARO = colors.HexColor("#F4F4F4")  # Fondos y filas alternas
COLOR_BLANCO = colors.HexColor("#FFFFFF")      # Fondo del documento
COLOR_ROJO_OSCURO = colors.HexColor("#B01220") # Énfasis puntual

BASE = Path(__file__).resolve().parents[2]

CARPETA_PDF = BASE / "Output" / "PDF"

RUTA_LOGO = BASE / "src" / "assets" / "talsa-logo.png"

def crear_estilos():
    estilos = getSampleStyleSheet()

    estilos.add(ParagraphStyle(
        name="titulo",
        parent=estilos["Title"],
        textColor=COLOR_TALSA,
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=15
    ))

    estilos.add(ParagraphStyle(
        name="seccion",
        parent=estilos["Heading2"],
        textColor=COLOR_TALSA,
        fontSize=12,
        spaceBefore=12,
        spaceAfter=8
    ))

    estilos.add(ParagraphStyle(
        name="normal",
        parent=estilos["BodyText"],
        textColor=COLOR_NEGRO,
        fontSize=9,
        leading=13
    ))

    estilos.add(ParagraphStyle(
        name="pequeno",
        parent=estilos["BodyText"],
        textColor=COLOR_NEGRO,
        fontSize=8,
        leading=10
    ))

    estilos.add(ParagraphStyle(
        name="lista",
        parent=estilos["BodyText"],
        textColor=COLOR_NEGRO,
        fontSize=9,
        leading=13,
        leftIndent=12
    ))

    estilos.add(ParagraphStyle(
    name="encabezado_tabla",
    parent=estilos["BodyText"],
    textColor=COLOR_BLANCO,
    fontSize=8,
    leading=10,
    fontName="Helvetica-Bold"
    ))

    return estilos

def crear_parrafo(texto, estilo):

    texto = html.escape(str(texto))

    return Paragraph(texto, estilo)


def crear_tabla(datos, anchos, estilos):

    tabla = Table(
        datos,
        colWidths=anchos,
        repeatRows=1
    )

    tabla.setStyle(TableStyle([

        # Encabezado
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_TALSA),
        ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_BLANCO),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        # Filas alternas
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [COLOR_BLANCO, COLOR_GRIS_CLARO]),

        # Texto
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("TEXTCOLOR", (0, 1), (-1, -1), COLOR_NEGRO),

        # Alineación y espacios
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),

        # Bordes
        ("GRID", (0, 0), (-1, -1), 0.4,
         colors.HexColor("#DDDDDD"))

    ]))

    return tabla


def crear_lista(elementos, estilo):

    contenido = []

    if not isinstance(elementos, list) or not elementos:
        return [crear_parrafo("No se registró información.", estilo)]

    for elemento in elementos:

        contenido.append(
            Paragraph("• " + html.escape(str(elemento)), estilo))

    return contenido

def extraer_especificaciones(ficha_tecnica, estilos):

    filas = [
        [
            crear_parrafo("Característica", estilos["encabezado_tabla"]),
            crear_parrafo("Especificación", estilos["encabezado_tabla"])
        ]
    ]

    for linea in str(ficha_tecnica).splitlines():

        linea = linea.strip()

        if not linea:
            continue

        if ":" in linea:

            caracteristica, especificacion = linea.split(":", 1)

        else:

            caracteristica = "Descripción"
            especificacion = linea

        filas.append([
            crear_parrafo(caracteristica, estilos["pequeno"]),
            crear_parrafo(especificacion, estilos["pequeno"])
        ])

    return filas


def crear_encabezado_pie(canvas, documento):
    canvas.saveState()

    ancho, alto = A4

    if RUTA_LOGO.exists():
        imagen = ImageReader(str(RUTA_LOGO))

        # Altura del logo: 2.5 cm
        alto_logo = 2.5 * cm

        proporcion = 613 / 551
        ancho_logo = alto_logo * proporcion

        # Ubicación: esquina superior izquierda
        x_logo = 2 * cm
        y_logo = alto - 3.2 * cm

        canvas.drawImage(
            imagen,
            x_logo,
            y_logo,
            width=ancho_logo,
            height=alto_logo,
            preserveAspectRatio=True,
            mask="auto"
        )
    else:
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(
            2 * cm,
            alto - 1.5 * cm,
            "LOGO TALSA"
        )

    # 2. Título del documento
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(COLOR_TALSA)

    canvas.drawRightString(
        ancho - 2 * cm,
        alto - 1.5 * cm,
        "INFORME TÉCNICO COMERCIAL"
    )

    # 3. Línea roja separadora
    canvas.setStrokeColor(COLOR_TALSA)
    canvas.setLineWidth(1.5)

    canvas.line(
        2 * cm,
        alto - 3.5 * cm,
        ancho - 2 * cm,
        alto - 3.5 * cm
    )

    # 4. Pie de página
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(COLOR_GRIS)

    canvas.drawString(
        2 * cm,
        1.2 * cm,
        "Talsa — Tecnología y Maquinaria para la industria alimentaria"
    )

    # 5. Número de página
    canvas.drawRightString(
        ancho - 2 * cm,
        1.2 * cm,
        f"Página {documento.page}"
    )

    canvas.restoreState()

def generar_informes(ventas_completas, df_resultados_ia):

    CARPETA_PDF.mkdir(parents=True, exist_ok=True)

    estilos = crear_estilos()

    # Organizar resultados de IA por identificador de venta
    resultados_por_venta = (df_resultados_ia.set_index("id_venta").to_dict("index"))

    informes_generados = 0

    for _, venta in ventas_completas.iterrows():

        id_venta = venta["id_venta"]

        # Buscar el análisis de IA correspondiente a la venta
        resultado = resultados_por_venta.get(id_venta)

        if resultado is None:
            print(f"No existe análisis de IA para la venta {id_venta}")
            continue

        # Nombre del archivo
        nombre_archivo = re.sub(
            r"[^A-Za-z0-9_-]",
            "_",
            str(id_venta)
        )

        ruta_pdf = CARPETA_PDF / f"Informe_{nombre_archivo}.pdf"

        # Crear documento
        documento = SimpleDocTemplate(
            str(ruta_pdf),
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=3.2 * cm,
            bottomMargin=2.2 * cm
        )

        contenido = []

        contenido.append(
            crear_parrafo("INFORME TÉCNICO COMERCIAL", estilos["titulo"]))

        contenido.append(Spacer(1, 8))

        contenido.append(
            crear_parrafo("1. Datos de facturación", estilos["seccion"]))

        fecha = venta["fecha_venta"]

        if pd.notna(fecha):
            fecha = fecha.strftime("%d/%m/%Y")
        else:
            fecha = "No disponible"

        monto = venta["monto_usd"]

        if pd.notna(monto):
            monto = f"USD {monto:,.2f}"
        else:
            monto = "No disponible"

        datos_facturacion = [
            ["Campo", "Información"],

            ["ID de venta", venta["id_venta"]],
            ["Empresa", venta["empresa"]],
            ["Industria", venta["industria"]],
            ["Equipo adquirido", venta["equipo_comprado"]],
            ["Fecha de venta", fecha],
            ["Monto", monto],
            ["Ubicación", venta["ubicacion"]]
        ]

        tabla_facturacion = [
            [
                crear_parrafo(fila[0], estilos["pequeno"]),
                crear_parrafo(fila[1], estilos["pequeno"])
            ]
            for fila in datos_facturacion
        ]

        contenido.append(
            crear_tabla(
                tabla_facturacion,
                [5 * cm, 11 * cm],
                estilos
            )
        )

        contenido.append(Spacer(1, 12))

        contenido.append(
            crear_parrafo(
                "2. Especificaciones técnicas del equipo",
                estilos["seccion"]
            )
        )

        especificaciones = extraer_especificaciones(
            venta["ficha_tecnica"],
            estilos
        )

        contenido.append(
            crear_tabla(
                especificaciones,
                [5 * cm, 11 * cm],
                estilos
            )
        )

        contenido.append(Spacer(1, 12))

        contenido.append(
            crear_parrafo(
                "3. Análisis de inteligencia artificial",
                estilos["seccion"]
            )
        )

        datos_analisis = [
            ["Indicador", "Resultado"],

            [
                "Score de compatibilidad",
                f"{resultado['score_compatibilidad']}/100"
            ],

            [
                "Complejidad de implementación",
                resultado["complejidad"]
            ]
        ]

        tabla_analisis = [
            [
                crear_parrafo(fila[0], estilos["pequeno"]),
                crear_parrafo(fila[1], estilos["pequeno"])
            ]
            for fila in datos_analisis
        ]

        contenido.append(
            crear_tabla(
                tabla_analisis,
                [7 * cm, 9 * cm],
                estilos
            )
        )

        contenido.append(Spacer(1, 8))

        # Justificación
        contenido.append(
            crear_parrafo(
                "Justificación del score",
                estilos["normal"]
            )
        )

        contenido.append(
            crear_parrafo(
                resultado.get(
                    "justificacion_score",
                    "No disponible"
                ),
                estilos["normal"]
            )
        )

        contenido.append(Spacer(1, 8))

        # Casos de uso
        contenido.append(
            crear_parrafo("Casos de uso", estilos["normal"])
        )

        contenido.extend(
            crear_lista(resultado["casos_uso"], estilos["lista"])
        )

        contenido.append(Spacer(1, 6))

        # Recomendaciones
        contenido.append(
            crear_parrafo(
                "Recomendaciones operativas",
                estilos["normal"]
            )
        )

        contenido.extend(
            crear_lista(
                resultado["recomendaciones_operativas"],
                estilos["lista"]
            )
        )

        contenido.append(Spacer(1, 6))

        # Limitaciones
        contenido.append(
            crear_parrafo(
                "Limitaciones técnicas",
                estilos["normal"]
            )
        )

        contenido.extend(
            crear_lista(
                resultado["limitaciones_tecnicas"],
                estilos["lista"]
            )
        )

        documento.build(contenido, onFirstPage=crear_encabezado_pie, onLaterPages=crear_encabezado_pie)

        informes_generados += 1

        print(f"Informe generado: {ruta_pdf}")

    print(
        f"\nProceso finalizado. "
        f"Informes generados: {informes_generados}"
    )

    return informes_generados

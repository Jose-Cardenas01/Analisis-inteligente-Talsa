import pandas as pd
import re
import unicodedata

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

def relacionar_datos(clientes_ventas, txt_catalogo, txt_cliente):
    
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

    bloques_perfil = re.split(r"\n\s*\n", txt_cliente.strip())

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

    return ventas_completas
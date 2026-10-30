def validar_resultado(resultado):

    campos_obligatorios = [
        "casos_uso",
        "recomendaciones_operativas",
        "limitaciones_tecnicas",
        "score_compatibilidad",
        "complejidad",
        "justificacion_score"
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

    if resultado["complejidad"] not in ["Alto", "Medio", "Bajo"]:
        raise ValueError("La complejidad debe ser Alto, Medio o Bajo")

    if (not isinstance(resultado["justificacion_score"], str) or not resultado["justificacion_score"].strip()):
        raise ValueError("La justificación debe ser un texto no vacío")

    return True
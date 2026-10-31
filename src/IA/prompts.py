def construir_prompt(ficha_tecnica, perfil_cliente):
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

    return prompt
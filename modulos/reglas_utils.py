from modulos.conexion import obtener_conexion

# ============================================================
# OBTENER REGLAS INTERNAS (ADAPTADO A TU TABLA reales)
# ============================================================
def obtener_reglas():
    """
    Devuelve un diccionario con los valores de reglas_internas.
    Si no hay registros, devuelve None.
    """

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            id_regla,
            Id_Grupo,
            nombre_grupo,
            nombre_comunidad,
            fecha_formacion,
            multa_inasistencia,
            ahorro_minimo,
            interes_por_10,
            prestamo_maximo,
            plazo_maximo,
            ciclo_inicio,
            ciclo_fin,
            meta_social,
            otras_reglas,
            permisos_inasistencia,
            multa_mora
        FROM reglas_internas
        ORDER BY id_regla DESC
        LIMIT 1
    """)

    reglas = cursor.fetchone()

    cursor.close()
    con.close()

    return reglas


# ============================================================
# GUARDAR / ACTUALIZAR REGLAS INTERNAS
# ============================================================
def guardar_reglas(
    nombre_grupo,
    nombre_comunidad,
    fecha_formacion,
    multa_inasistencia,
    ahorro_minimo,
    interes_por_10,
    prestamo_maximo,
    plazo_maximo,
    ciclo_inicio,
    ciclo_fin,
    meta_social,
    otras_reglas,
    permisos_inasistencia,
    multa_mora,
    Id_Grupo=1,
):
    """
    Actualiza el último registro o crea uno nuevo.
    """

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Verificar si ya hay registro
    cursor.execute("SELECT id_regla FROM reglas_internas ORDER BY id_regla DESC LIMIT 1")
    row = cursor.fetchone()

    if row:
        # ACTUALIZAR
        cursor.execute("""
            UPDATE reglas_internas
            SET
                nombre_grupo=%s,
                nombre_comunidad=%s,
                fecha_formacion=%s,
                multa_inasistencia=%s,
                ahorro_minimo=%s,
                interes_por_10=%s,
                prestamo_maximo=%s,
                plazo_maximo=%s,
                ciclo_inicio=%s,
                ciclo_fin=%s,
                meta_social=%s,
                otras_reglas=%s,
                permisos_inasistencia=%s,
                multa_mora=%s,
                Id_Grupo=%s
            WHERE id_regla=%s
        """, (
            nombre_grupo,
            nombre_comunidad,
            fecha_formacion,
            multa_inasistencia,
            ahorro_minimo,
            interes_por_10,
            prestamo_maximo,
            plazo_maximo,
            ciclo_inicio,
            ciclo_fin,
            meta_social,
            otras_reglas,
            permisos_inasistencia,
            multa_mora,
            Id_Grupo,
            row["id_regla"]
        ))

    else:
        # CREAR NUEVO
        cursor.execute("""
            INSERT INTO reglas_internas(
                Id_Grupo, nombre_grupo, nombre_comunidad, fecha_formacion,
                multa_inasistencia, ahorro_minimo, interes_por_10,
                prestamo_maximo, plazo_maximo, ciclo_inicio, ciclo_fin,
                meta_social, otras_reglas, permisos_inasistencia, multa_mora
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            Id_Grupo,
            nombre_grupo,
            nombre_comunidad,
            fecha_formacion,
            multa_inasistencia,
            ahorro_minimo,
            interes_por_10,
            prestamo_maximo,
            plazo_maximo,
            ciclo_inicio,
            ciclo_fin,
            meta_social,
            otras_reglas,
            permisos_inasistencia,
            multa_mora
        ))

    con.commit()
    cursor.close()
    con.close()


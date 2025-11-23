from modulos.conexion import obtener_conexion

def obtener_reglas():
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo LIMIT 1")
    reglas = cursor.fetchone()

    cursor.close()
    con.close()

    if not reglas:
        return None

    # Convertir claves a un dict limpio de Python
    return {
        "multa_inasistencia": float(reglas.get("multa_inasistencia", 0)),
        "ahorro_minimo": float(reglas.get("ahorro_minimo", 0)),
        "interes_por_10": float(reglas.get("interes_por_10", 0)),
        "prestamo_maximo": float(reglas.get("prestamo_maximo", 0)),
        "plazo_maximo": int(reglas.get("plazo_maximo", 0)),
        "permisos_validos": reglas.get("permisos_inasistencia", "enfermedad, trabajo").strip(),
        "multa_mora": float(reglas.get("multa_mora", 0)),   # ← NUEVO CAMPO
    }




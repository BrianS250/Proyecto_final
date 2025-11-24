import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# OBTENER CICLO ACTIVO
# ---------------------------------------------------------
def obtener_ciclo_activo():
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM ciclo_resumen
        WHERE fecha_cierre IS NULL
        ORDER BY id_ciclo_resumen DESC
        LIMIT 1
    """)
    ciclo = cur.fetchone()
    con.close()
    return ciclo


# ---------------------------------------------------------
# SALDO INICIAL (primer registro de caja dentro del ciclo)
# ---------------------------------------------------------
def obtener_saldo_inicial(fecha_inicio):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT saldo_inicial 
        FROM caja_reunion
        WHERE fecha >= %s
        ORDER BY fecha ASC
        LIMIT 1
    """, (fecha_inicio,))
    fila = cur.fetchone()

    con.close()
    return fila[0] if fila else 0


# ---------------------------------------------------------
# SALDO FINAL (último registro de caja dentro del ciclo)
# ---------------------------------------------------------
def obtener_saldo_final(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha_inicio, fecha_fin))
    fila = cur.fetchone()

    con.close()
    return fila[0] if fila else 0


# ---------------------------------------------------------
# RESUMEN DE MOVIMIENTOS REALES DEL CICLO
# ---------------------------------------------------------
def obtener_totales(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    # TOTAL INGRESOS
    cur.execute("""
        SELECT COALESCE(SUM(ingresos), 0)
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    ingresos = cur.fetchone()[0]

    # TOTAL EGRESOS
    cur.execute("""
        SELECT COALESCE(SUM(egresos), 0)
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    egresos = cur.fetchone()[0]

    # PRESTAMOS OTORGADOS
    cur.execute("""
        SELECT COALESCE(SUM(Monto), 0)
        FROM prestamo
        WHERE Fecha_prestamo BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    prestados = cur.fetchone()[0]

    # PAGOS DE PRÉSTAMO
    cur.execute("""
        SELECT COALESCE(SUM(Monto_pagado), 0)
        FROM pago_prestamo
        WHERE Fecha_pago BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    pagados = cur.fetchone()[0]

    # MULTAS APLICADAS
    cur.execute("""
        SELECT COALESCE(SUM(Monto), 0)
        FROM multa
        WHERE Fecha_aplicacion BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    multas = cur.fetchone()[0]

    # AHORRO DE SOCIAS
    cur.execute("""
        SELECT COALESCE(SUM(Monto), 0)
        FROM ahorro
        WHERE Fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    ahorro = cur.fetchone()[0]

    con.close()

    return ingresos, egresos, prestados, pagados, multas, ahorro


# ---------------------------------------------------------
# INTERFAZ PRINCIPAL DE CIERRE DE CICLO
# ---------------------------------------------------------
def cierre_ciclo():
    st.title("🔒 Cierre de Ciclo — Solidaridad CVX")

    ciclo = obtener_ciclo_activo()

    # NO HAY CICLO ACTIVO
    if ciclo is None:
        st.warning("❌ No existe ningún ciclo activo. Debes iniciar uno primero.")
        return

    fecha_inicio = ciclo["fecha_inicio"]
    fecha_fin = date.today().strftime("%Y-%m-%d")

    st.info(f"📅 Ciclo iniciado el: **{fecha_inicio}**")

    # Totales del ciclo
    ingresos, egresos, prestados, pagados, multas, ahorro = obtener_totales(fecha_inicio, fecha_fin)

    # Saldos
    saldo_inicial = obtener_saldo_inicial(fecha_inicio)
    saldo_final = obtener_saldo_final(fecha_inicio, fecha_fin)

    # -----------------------------
    # RESUMEN VISUAL
    # -----------------------------
    st.subheader("📘 Resumen del ciclo:")

    st.write(f"**Saldo inicial:** ${saldo_inicial:,.2f}")
    st.write(f"**Saldo final:** ${saldo_final:,.2f}")
    st.write("---")
    st.write(f"**Total ingresos:** ${ingresos:,.2f}")
    st.write(f"**Total egresos:** ${egresos:,.2f}")
    st.write(f"**Préstamos otorgados:** ${prestados:,.2f}")
    st.write(f"**Préstamos pagados:** ${pagados:,.2f}")
    st.write(f"**Multas aplicadas:** ${multas:,.2f}")
    st.write(f"**Ahorro de socias:** ${ahorro:,.2f}")

    st.warning("🟠 Verifica la información antes de cerrar el ciclo. Este proceso es definitivo.")

    # -----------------------------
    # BOTÓN DE CIERRE
    # -----------------------------
    if st.button("🔐 Cerrar ciclo ahora"):
        con = obtener_conexion()
        cur = con.cursor()

        cur.execute("""
            UPDATE ciclo_resumen
            SET fecha_cierre=%s,
                saldo_inicial=%s,
                saldo_final=%s,
                total_ingresos=%s,
                total_egresos=%s,
                total_prestamos_otorgados=%s,
                total_prestamos_pagados=%s,
                total_multa=%s,
                total_ahorro=%s
            WHERE id_ciclo_resumen=%s
        """, (
            fecha_fin,
            saldo_inicial,
            saldo_final,
            ingresos,
            egresos,
            prestados,
            pagados,
            multas,
            ahorro,
            ciclo["id_ciclo_resumen"]
        ))

        con.commit()
        con.close()

        st.success("✅ Ciclo cerrado correctamente.")
        st.balloons()

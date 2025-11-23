import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.reglas_utils import obtener_reglas


def cierre_ciclo():

    st.title("🔴 Cierre del Ciclo General – Solidaridad CVX")

    # ======================================================
    # 1️⃣ LEER REGLAS INTERNAS (FECHAS DEL CICLO)
    # ======================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No existen reglas internas registradas. Debes definirlas primero.")
        return

    fecha_inicio_reg = reglas.get("fecha_inicio_ciclo")
    fecha_fin_reg = reglas.get("fecha_fin_ciclo")

    if not fecha_inicio_reg:
        st.error("⚠ Debes definir la fecha de inicio del ciclo en Reglas Internas.")
        return

    st.info(f"📌 Ciclo según reglamento: **{fecha_inicio_reg} → {fecha_fin_reg or 'Activo'}**")

    # ======================================================
    # 2️⃣ CONEXIÓN
    # ======================================================
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ======================================================
    # 3️⃣ INGRESOS DEL CICLO
    # ======================================================

    # Multas pagadas
    cursor.execute("""
        SELECT IFNULL(SUM(Monto),0) AS total
        FROM Multa
        WHERE Estado='Pagada'
          AND Fecha_aplicacion >= %s
    """, (fecha_inicio_reg,))
    total_multas = cursor.fetchone()["total"]

    # Ingresos extraordinarios
    cursor.execute("""
        SELECT IFNULL(SUM(Monto),0) AS total
        FROM IngresosExtra
        WHERE Fecha >= %s
    """, (fecha_inicio_reg,))
    total_ing_extra = cursor.fetchone()["total"]

    # Pagos de préstamo (suma de cuotas pagadas)
    cursor.execute("""
        SELECT IFNULL(SUM(Monto_cuota),0) AS total
        FROM Cuotas_prestamo
        WHERE Estado='pagada'
          AND Fecha_pago >= %s
    """, (fecha_inicio_reg,))
    total_pagos = cursor.fetchone()["total"]

    total_ingresos = total_multas + total_ing_extra + total_pagos

    # ======================================================
    # 4️⃣ EGRESOS DEL CICLO (PRÉSTAMOS OTORGADOS)
    # ======================================================
    cursor.execute("""
        SELECT IFNULL(SUM(`Monto prestado`),0) AS total
        FROM Prestamo
        WHERE `Fecha del préstamo` >= %s
    """, (fecha_inicio_reg,))
    total_prestamos = cursor.fetchone()["total"]

    total_egresos = total_prestamos

    # ======================================================
    # 5️⃣ RESULTADOS
    # ======================================================
    monto_repartido = total_ingresos - total_egresos

    st.subheader("📊 Resumen del ciclo")
    st.write(f"💰 **Total ingresos:** ${total_ingresos:,.2f}")
    st.write(f"🏛 **Total egresos:** ${total_egresos:,.2f}")
    st.success(f"🧮 **Monto a repartir:** ${monto_repartido:,.2f}")
    st.info("📌 El saldo final del ciclo se reinicia a **$0.00** porque todo se reparte.")

    # ======================================================
    # 6️⃣ CERRAR CICLO (ACTUALIZAR SOLO REGLAS INTERNAS)
    # ======================================================
    if st.button("🔒 Cerrar ciclo con estas condiciones"):

        cursor.execute("""
            UPDATE reglas_internas
            SET fecha_fin_ciclo = %s
            ORDER BY id_regla DESC
            LIMIT 1
        """, (date.today(),))

        con.commit()

        st.success("✔ Ciclo cerrado correctamente. Fecha final actualizada en reglas internas.")
        st.rerun()


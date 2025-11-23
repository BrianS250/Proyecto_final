import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.reglas_utils import obtener_reglas


def cierre_ciclo():

    st.title("🔴 Cierre del Ciclo General – Solidaridad CVX")

    # ======================================================
    # 1️⃣ LEER REGLAS INTERNAS PARA OBTENER FECHAS DE CICLO
    # ======================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No existen reglas internas registradas. Debes definirlas primero.")
        return

    fecha_inicio_reg = reglas["fecha_inicio_ciclo"]
    fecha_fin_reg = reglas["fecha_fin_ciclo"]

    if not fecha_inicio_reg:
        st.error("⚠ Debes definir la fecha de inicio del ciclo en Reglas Internas.")
        return

    st.info(f"📌 Ciclo según reglamento: **{fecha_inicio_reg} → {fecha_fin_reg or 'Activo'}**")

    # ======================================================
    # 2️⃣ CONEXIÓN A BD
    # ======================================================
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ======================================================
    # 3️⃣ CALCULAR INGRESOS DEL CICLO
    # ======================================================
    cursor.execute("""
        SELECT IFNULL(SUM(Monto),0) AS total
        FROM Multa
        WHERE Estado='Pagada'
          AND Fecha_aplicacion >= %s
    """, (fecha_inicio_reg,))
    total_multas = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT IFNULL(SUM(Monto),0) AS total
        FROM IngresosExtra
        WHERE Fecha >= %s
    """, (fecha_inicio_reg,))
    total_ing_extra = cursor.fetchone()["total"]

    # PAGOS DE PRÉSTAMO (interés + capital)
    cursor.execute("""
        SELECT IFNULL(SUM(Monto_cuota),0) AS total
        FROM Cuotas_prestamo
        WHERE Estado='pagada'
          AND Fecha_pago >= %s
    """, (fecha_inicio_reg,))
    total_pagos = cursor.fetchone()["total"]

    total_ingresos = total_multas + total_ing_extra + total_pagos

    # ======================================================
    # 4️⃣ EGRESOS DEL CICLO (solo préstamos otorgados)
    # ======================================================
    cursor.execute("""
        SELECT IFNULL(SUM(`Monto prestado`),0) AS total
        FROM Prestamo
        WHERE `Fecha del préstamo` >= %s
    """, (fecha_inicio_reg,))
    total_prestamos = cursor.fetchone()["total"]

    total_egresos = total_prestamos

    # ======================================================
    # 5️⃣ SALDOS
    # ======================================================
    monto_repartido = total_ingresos - total_egresos
    saldo_final = 0.00  # siempre reinicia

    st.subheader("📊 Resumen del ciclo")

    st.write(f"💰 **Total ingresos:** ${total_ingresos:,.2f}")
    st.write(f"🏦 **Total egresos:** ${total_egresos:,.2f}")
    st.success(f"🧮 **Monto a repartir en cierre:** ${monto_repartido:,.2f}")
    st.info("📌 El saldo final del ciclo queda en **$0.00** ya que todo se reparte.")

    # ======================================================
    # 6️⃣ FINALIZAR CICLO
    # ======================================================
    if st.button("🔒 Cerrar ciclo con estas condiciones"):

        cursor.execute("""
            UPDATE reglas_internas
            SET fecha_fin_ciclo = %s
            ORDER BY id_regla DESC
            LIMIT 1
        """, (date.today(),))

        con.commit()

        st.success("✔ Ciclo cerrado correctamente y fecha final registrada.")
        st.rerun()

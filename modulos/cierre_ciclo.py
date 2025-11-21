import streamlit as st
from datetime import date
from modulos.config.conexion import obtener_conexion

def cierre_ciclo():

    st.title("🔴 Cierre del Ciclo General – Solidaridad CVX")

    con = obtener_conexion()
    cursor = con.cursor()

    # 1️⃣ CICLO ACTIVO
    cursor.execute("SELECT id_ciclo, nombre_ciclo, fecha_inicio FROM ciclo WHERE estado='abierto'")
    ciclo = cursor.fetchone()

    if not ciclo:
        st.error("❌ No existe un ciclo activo. Debes abrir uno primero.")
        return

    id_ciclo, nombre_ciclo, fecha_inicio = ciclo

    st.info(f"📌 Ciclo activo: **{nombre_ciclo}** (Inició el {fecha_inicio})")

    # 2️⃣ INGRESOS DEL CICLO
    cursor.execute("""
        SELECT IFNULL(SUM(Monto),0)
        FROM Multa
        WHERE Estado='Pagada'
    """)
    total_multas = cursor.fetchone()[0]

    cursor.execute("""
        SELECT IFNULL(SUM(Monto),0)
        FROM IngresosExtra
    """)
    total_ing_extra = cursor.fetchone()[0]

    # 🔧 TABLA Y COLUMNAS CORRECTAS (con espacios y tildes)
    cursor.execute("""
        SELECT IFNULL(SUM(`Monto abonado` + `Interés pagado`),0)
        FROM `Pago del prestamo`
    """)
    total_pagos = cursor.fetchone()[0]

    total_ingresos = total_multas + total_ing_extra + total_pagos

    # 3️⃣ EGRESOS DEL CICLO
    cursor.execute("""
        SELECT IFNULL(SUM(Monto_prestado),0)
        FROM Prestamo
    """)
    total_prestamos = cursor.fetchone()[0]

    total_egresos = total_prestamos

    # 4️⃣ TOTALES
    monto_repartido = total_ingresos - total_egresos
    saldo_final = 0.00

    st.subheader("📊 Resumen del ciclo")

    st.write(f"💰 **Total ingresos:** ${total_ingresos:,.2f}")
    st.write(f"🏦 **Total egresos:** ${total_egresos:,.2f}")
    st.success(f"🧮 **Monto a repartir:** ${monto_repartido:,.2f}")
    st.info("📌 El saldo final del ciclo queda en **$0.00** porque todo se reparte.")

    # 5️⃣ CIERRE
    if st.button("🔒 Cerrar ciclo ahora"):

        cursor.execute("""
            UPDATE ciclo
            SET fecha_fin=%s,
                saldo_final=%s,
                estado='cerrado'
            WHERE id_ciclo=%s
        """, (date.today(), saldo_final, id_ciclo))

        con.commit()

        st.success("✔ Ciclo cerrado correctamente.")
        st.rerun()

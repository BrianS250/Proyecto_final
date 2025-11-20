import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# Crear o recuperar la reunión del día
# ---------------------------------------------------------
def obtener_o_crear_reunion(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (fecha,))
        reunion = cursor.fetchone()

        if reunion:
            return reunion["id_caja"]

        cursor.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
        ultimo = cursor.fetchone()
        saldo_anterior = ultimo["saldo_final"] if ultimo else 0

        cursor.execute("""
            INSERT INTO caja_reunion (fecha, saldo_inicial, ingresos, egresos, saldo_final)
            VALUES (%s, %s, 0, 0, %s)
        """, (fecha, saldo_anterior, saldo_anterior))

        con.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        con.close()


# ---------------------------------------------------------
# Registrar movimiento en caja
# ---------------------------------------------------------
def registrar_movimiento(id_caja, tipo, categoria, monto):
    con = obtener_conexion()
    cursor = con.cursor()

    try:
        cursor.execute("""
            INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
            VALUES (%s, %s, %s, %s)
        """, (id_caja, tipo, categoria, monto))

        if tipo == "Ingreso":
            cursor.execute("""
                UPDATE caja_reunion
                SET ingresos = ingresos + %s,
                    saldo_final = saldo_final + %s
                WHERE id_caja = %s
            """, (monto, monto, id_caja))

        else:
            cursor.execute("""
                UPDATE caja_reunion
                SET egresos = egresos + %s,
                    saldo_final = saldo_final - %s
                WHERE id_caja = %s
            """, (monto, monto, id_caja))

        con.commit()

    finally:
        cursor.close()
        con.close()


# ---------------------------------------------------------
# Obtener saldo actual global
# ---------------------------------------------------------
def obtener_saldo_actual():
    con = obtener_conexion()
    cursor = con.cursor()

    try:
        cursor.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
        dato = cursor.fetchone()
        return dato[0] if dato else 0
    finally:
        cursor.close()
        con.close()


# ---------------------------------------------------------
# Mostrar reporte de caja
# ---------------------------------------------------------
def mostrar_reporte_caja():
    st.subheader("📊 Reporte de Caja por Reunión")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
        fechas = [f["fecha"] for f in cursor.fetchall()]

        if not fechas:
            st.info("Aún no hay reuniones registradas.")
            return

        fecha_sel = st.selectbox("📅 Seleccione la fecha de reunión:", fechas)

        cursor.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (fecha_sel,))
        data = cursor.fetchone()

        if not data:
            st.warning("No se encontró información para esa fecha.")
            return

        st.markdown("### 📘 Resumen del Día")

        col1, col2, col3 = st.columns(3)
        col1.metric("Saldo Inicial", f"${data['saldo_inicial']:.2f}")
        col2.metric("Ingresos del Día", f"${data['ingresos']:.2f}")
        col3.metric("Egresos del Día", f"${data['egresos']:.2f}")

        st.markdown("### 💰 Saldo Final")
        st.metric("", f"${data['saldo_final']:.2f}")

        cursor.execute("""
            SELECT tipo, categoria, monto
            FROM caja_movimientos
            WHERE id_caja = %s
            ORDER BY id_mov DESC
        """, (data["id_caja"],))

        movimientos = cursor.fetchall()

        st.markdown("### 📄 Detalle de Movimientos")
        st.table(movimientos)

    finally:
        cursor.close()
        con.close()

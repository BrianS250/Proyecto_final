import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


# -------------------------------------------------
# FUNCIONES DE CAJA
# -------------------------------------------------
def obtener_saldo_por_fecha(fecha):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # 1. Buscar reunión exacta
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        return reunion["saldo_final"]

    # 2. Si no existe, usamos el último saldo previo
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha < %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    anterior = cursor.fetchone()

    return anterior["saldo_final"] if anterior else 0



def registrar_gasto(fecha, descripcion, monto):
    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("""
        INSERT INTO caja_gastos (fecha, descripcion, monto)
        VALUES (%s, %s, %s)
    """, (fecha, descripcion, monto))
    con.commit()

    # Actualizar egresos y saldo_final de la reunión
    cursor.execute("""
        SELECT id_caja, ingresos, egresos, saldo_inicial
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        id_caja = reunion[0]
        ingresos = reunion[1]
        egresos = reunion[2] + monto
        saldo_final = reunion[3] + ingresos - egresos

        cursor.execute("""
            UPDATE caja_reunion
            SET egresos = %s, saldo_final = %s
            WHERE id_caja = %s
        """, (egresos, saldo_final, id_caja))
        con.commit()



# -------------------------------------------------
# PANEL DE LA DIRECTIVA
# -------------------------------------------------
def interfaz_directiva():

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # ---------------------------
    # SELECCIÓN DE FECHA
    # ---------------------------
    st.subheader("📅 Seleccione la fecha de reunión del reporte:")

    fecha_reporte = st.date_input("Fecha del reporte", value=date.today())

    saldo = obtener_saldo_por_fecha(fecha_reporte)

    st.info(f"🪙 Saldo de caja para {fecha_reporte}: **${saldo:,.2f}**")

    st.write("---")

    # ---------------------------
    # REGISTRO DE GASTOS
    # ---------------------------
    st.subheader("🧾 Registrar gastos del grupo")

    fecha_gasto = st.date_input("Fecha del gasto", value=fecha_reporte)
    descripcion = st.text_input("Descripción del gasto")
    monto = st.number_input("Monto del gasto", min_value=0.00, step=0.25)

    if st.button("💸 Registrar gasto"):
        if descripcion.strip() == "":
            st.warning("⚠️ Debe ingresar una descripción.")
        elif monto <= 0:
            st.warning("⚠️ El monto debe ser mayor a 0.")
        else:
            registrar_gasto(fecha_gasto, descripcion, monto)
            st.success("✅ Gasto registrado correctamente.")
            st.rerun()

    st.write("---")

    # ---------------------------
    # CONSULTA DE GASTOS
    # ---------------------------
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT fecha, descripcion, monto
        FROM caja_gastos
        ORDER BY fecha DESC
    """)

    gastos = cursor.fetchall()

    st.subheader("📋 Gastos registrados")
    if gastos:
        st.table(gastos)
    else:
        st.info("Aún no hay gastos registrados.")

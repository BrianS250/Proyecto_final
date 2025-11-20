import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion

def reporte_caja():

    st.title("📊 Reporte de Caja por Reunión")

    con = obtener_conexion()
    cursor = con.cursor()

    # ---------------------------------------------------------
    # FECHA SELECCIONADA
    # ---------------------------------------------------------
    fechas = []

    cursor.execute("SELECT DISTINCT Fecha FROM Caja ORDER BY Fecha DESC")
    fechas_raw = cursor.fetchall()

    if fechas_raw:
        fechas = [f[0] for f in fechas_raw]

    if not fechas:
        st.info("Aún no hay registros en caja.")
        return

    fecha_sel = st.selectbox("📅 Seleccione la fecha de reunión:", fechas)

    # ---------------------------------------------------------
    # SALDO INICIAL
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT Saldo_actual 
        FROM Caja 
        WHERE Fecha < %s
        ORDER BY Id_Caja DESC LIMIT 1
    """, (fecha_sel,))

    row = cursor.fetchone()
    saldo_inicial = row[0] if row else 0

    # ---------------------------------------------------------
    # MOVIMIENTOS DEL DÍA
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT Concepto, Monto, Saldo_actual, Id_Tipo_movimiento
        FROM Caja
        WHERE Fecha = %s
        ORDER BY Id_Caja ASC
    """, (fecha_sel,))

    movimientos = cursor.fetchall()

    if not movimientos:
        st.warning("No hay movimientos registrados en esta fecha.")
        return

    df = pd.DataFrame(movimientos, columns=["Concepto", "Monto", "Saldo Posterior", "Tipo"])

    # Entradas (Id_Tipo_movimiento = 2)
    ingresos = df[df["Tipo"] == 2]["Monto"].sum()

    # Salidas (Id_Tipo_movimiento = 3)
    egresos = df[df["Tipo"] == 3]["Monto"].sum() * -1  # egresos son negativos

    # Saldo final
    saldo_final = saldo_inicial + ingresos - egresos

    # ---------------------------------------------------------
    # MOSTRAR RESUMEN
    # ---------------------------------------------------------
    st.subheader("📘 Resumen del Día")

    col1, col2, col3 = st.columns(3)

    col1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    col2.metric("Ingresos del Día", f"${ingresos:.2f}")
    col3.metric("Egresos del Día", f"${egresos:.2f}")

    st.metric("💰 Saldo Final", f"${saldo_final:.2f}")

    st.markdown("---")

    # ---------------------------------------------------------
    # DETALLE DE MOVIMIENTOS
    # ---------------------------------------------------------
    st.subheader("📋 Detalle de Movimientos")

    df_display = df.copy()
    df_display["Monto"] = df_display["Monto"].apply(lambda x: f"${x:.2f}")
    df_display["Saldo Posterior"] = df_display["Saldo Posterior"].apply(lambda x: f"${x:.2f}")

    tipo_map = {2: "Ingreso", 3: "Egreso"}
    df_display["Tipo"] = df_display["Tipo"].map(tipo_map)

    st.dataframe(df_display)

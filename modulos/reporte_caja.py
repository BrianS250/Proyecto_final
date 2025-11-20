import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

# Importar funciones del nuevo sistema de caja
from modulos.caja import obtener_o_crear_reunion


# ============================================================
# REPORTE DE CAJA POR REUNIÓN
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja por Reunión")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ---------------------------------------------------------
    # CREAR REUNIÓN DE HOY SI NO EXISTE
    # ---------------------------------------------------------
    hoy = date.today().strftime("%Y-%m-%d")
    obtener_o_crear_reunion(hoy)

    # ---------------------------------------------------------
    # LISTA DE FECHAS DISPONIBLES
    # ---------------------------------------------------------
    cursor.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
    fechas_raw = cursor.fetchall()

    if not fechas_raw:
        st.info("Aún no hay reuniones registradas en caja.")
        return

    fechas = [fila["fecha"] for fila in fechas_raw]

    fecha_sel = st.selectbox("📅 Seleccione la fecha de reunión:", fechas)

    # ---------------------------------------------------------
    # OBTENER RESUMEN DE LA FECHA SELECCIONADA
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT *
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha_sel,))
    
    reunion = cursor.fetchone()

    if not reunion:
        st.warning("No se encontró información de caja para esta fecha.")
        return

    saldo_inicial = float(reunion["saldo_inicial"])
    ingresos = float(reunion["ingresos"])
    egresos = float(reunion["egresos"])
    saldo_final = float(reunion["saldo_final"])

    # ---------------------------------------------------------
    # MOSTRAR RESUMEN
    # ---------------------------------------------------------
    st.subheader("📘 Resumen del Día")

    col1, col2, col3 = st.columns(3)

    col1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    col2.metric("Ingresos del Día", f"${ingresos:.2f}")
    col3.metric("Egresos del Día", f"${egresos:.2f}")

    st.markdown("### 💰 Saldo Final")
    st.metric("", f"${saldo_final:.2f}")

    st.markdown("---")

    # ---------------------------------------------------------
    # DETALLE DE MOVIMIENTOS
    # ---------------------------------------------------------
    st.subheader("📋 Detalle de Movimientos del Día")

    cursor.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja = %s
        ORDER BY id_mov ASC
    """, (reunion["id_caja"],))

    movimientos = cursor.fetchall()

    if not movimientos:
        st.info("No hay movimientos registrados para esta reunión.")
        return

    df = pd.DataFrame(movimientos)

    df["monto"] = df["monto"].apply(lambda x: f"${x:.2f}")

    st.dataframe(df)

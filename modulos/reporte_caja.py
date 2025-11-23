import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

# Sistema de caja
from modulos.caja import obtener_o_crear_reunion

# Reglas internas (para ciclo)
from modulos.reglas_utils import obtener_reglas


# ============================================================
# REPORTE DE CAJA POR REUNIÓN — COMPLETO E INTEGRADO
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ LEER CICLO (FECHA INICIO DESDE REGLAMENTO)
    # ============================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ Debes registrar primero las reglas internas.")
        return

    fecha_inicio_ciclo = reglas.get("fecha_inicio_ciclo", None)

    if not fecha_inicio_ciclo:
        st.error("⚠ Debes definir fecha de inicio del ciclo en Reglas Internas.")
        return

    # ============================================================
    # 2️⃣ CREAR REUNIÓN DE HOY SI NO EXISTE
    # ============================================================
    hoy = date.today().strftime("%Y-%m-%d")
    obtener_o_crear_reunion(hoy)

    # ============================================================
    # 3️⃣ LISTA DE REUNIONES DISPONIBLES
    # ============================================================
    cursor.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
    fechas_raw = cursor.fetchall()

    if not fechas_raw:
        st.info("Aún no hay reuniones registradas.")
        return

    fechas = [fila["fecha"] for fila in fechas_raw]

    fecha_sel = st.selectbox("📅 Seleccione la fecha:", fechas)

    # ============================================================
    # 4️⃣ RESUMEN DEL DÍA SELECCIONADO
    # ============================================================
    cursor.execute("""
        SELECT *
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha_sel,))
    
    reunion = cursor.fetchone()

    if not reunion:
        st.warning("No se encontró información de caja para esta fecha.")
        return

    id_caja = reunion["id_caja"]
    saldo_inicial = float(reunion["saldo_inicial"])
    ingresos = float(reunion["ingresos"])
    egresos = float(reunion["egresos"])
    saldo_final = float(reunion["saldo_final"])

    st.subheader("📘 Resumen del día")

    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    col2.metric("Ingresos", f"${ingresos:.2f}")
    col3.metric("Egresos", f"${egresos:.2f}")

    st.metric("💰 Saldo Final del Día", f"${saldo_final:.2f}")

    st.markdown("---")

    # ============================================================
    # 5️⃣ DETALLE DE MOVIMIENTOS DEL DÍA
    # ============================================================
    st.subheader("📋 Movimientos del día")

    cursor.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja = %s
        ORDER BY id_mov ASC
    """, (id_caja,))

    movimientos = cursor.fetchall()

    if not movimientos:
        st.info("No hay movimientos registrados en esta reunión.")
    else:
        df = pd.DataFrame(movimientos)
        df["monto"] = df["monto"].apply(lambda x: f"${x:.2f}")
        st.dataframe(df, hide_index=True)

    st.markdown("---")

    # ============================================================
    # 6️⃣ RESUMEN ACUMULADO DEL CICLO
    # ============================================================
    st.subheader("📊 Resumen del ciclo (desde reglas internas)")

    cursor.execute("""
        SELECT 
            IFNULL(SUM(ingresos), 0) AS total_ingresos,
            IFNULL(SUM(egresos), 0) AS total_egresos
        FROM caja_reunion
        WHERE fecha >= %s
    """, (fecha_inicio_ciclo,))

    totales_ciclo = cursor.fetchone()
    total_ingresos_ciclo = float(totales_ciclo["total_ingresos"])
    total_egresos_ciclo = float(totales_ciclo["total_egresos"])

    st.write(f"📥 **Ingresos acumulados:** ${total_ingresos_ciclo:.2f}")
    st.write(f"📤 **Egresos acumulados:** ${total_egresos_ciclo:.2f}")

    st.success(f"💼 **Balance del ciclo:** ${total_ingresos_ciclo - total_egresos_ciclo:.2f}")

    st.info("📌 Este balance coincide automáticamente con los datos usados en 'Cerrar ciclo'.")

    cursor.close()
    con.close()

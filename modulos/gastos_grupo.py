import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_por_fecha


def gastos_grupo():

    st.title("🧾 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # RESPONSABLE DEL GASTO
    # --------------------------------------------------------
    responsable = st.text_input("👤 Nombre de la persona responsable del gasto")

    # DUI SOLO 9 NÚMEROS
    dui_input = st.text_input("DUI (9 dígitos)", max_chars=9)

    if dui_input and (not dui_input.isdigit() or len(dui_input) > 9):
        st.warning("⚠️ El DUI debe contener solo números y un máximo de 9 dígitos.")
        return

    # Formato final del DUI para la base de datos (8 dígitos + guion + dígito)
    dui_formateado = dui_input[:8] + "-" + dui_input[8:] if len(dui_input) == 9 else None

    # --------------------------------------------------------
    # DESCRIPCIÓN DEL GASTO
    # --------------------------------------------------------
    descripcion = st.text_input("Descripción del gasto")

    # --------------------------------------------------------
    # MONTO DEL GASTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($)", min_value=0.25, step=0.25)

    # --------------------------------------------------------
    # SALDO DISPONIBLE EN CAJA
    # --------------------------------------------------------
    saldo = obtener_saldo_por_fecha(fecha)
    st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo:.2f}**")

    # --------------------------------------------------------
    # BOTÓN PARA REGISTRAR GASTO
    # --------------------------------------------------------
    if st.button("💳 Registrar gasto"):

        # NO MOSTRAR MENSAJE – SOLO BLOQUEAR EL REGISTRO
        if monto > saldo:
            return

        # Obtener Id_Caja de la reunión
        id_caja = obtener_o_crear_reunion(fecha)

        # Registrar gasto en tabla Gastos_grupo
        cursor.execute("""
            INSERT INTO Gastos_grupo(Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (fecha, descripcion, monto, responsable, dui_formateado, id_caja))
        con.commit()

        # Registrar movimiento en caja (egreso)
        registrar_movimiento(id_caja, "Egreso", f"Gasto – {descripcion}", monto)

        st.success("✔ Gasto registrado correctamente.")
        st.rerun()

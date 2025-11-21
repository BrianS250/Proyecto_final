import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
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
    # RESPONSABLE
    # --------------------------------------------------------
    responsable = st.text_input("👤 Nombre de la persona responsable del gasto")

    # --------------------------------------------------------
    # DUI – OBLIGATORIO, EXACTO 9 NÚMEROS
    # --------------------------------------------------------
    dui_input = st.text_input("DUI (9 dígitos)", max_chars=9)

    # --------------------------------------------------------
    # CONCEPTO / DESCRIPCIÓN – OPCIONAL
    # --------------------------------------------------------
    descripcion = st.text_input("Concepto del gasto (opcional)")

    # --------------------------------------------------------
    # MONTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($)", min_value=0.25, step=0.25)

    # --------------------------------------------------------
    # SALDO DISPONIBLE
    # --------------------------------------------------------
    saldo = obtener_saldo_por_fecha(fecha)
    st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo:.2f}**")

    # --------------------------------------------------------
    # BOTÓN PARA REGISTRO
    # --------------------------------------------------------
    if st.button("💳 Registrar gasto"):

        # =======================
        # VALIDACIONES
        # =======================

        # Responsable
        if not responsable.strip():
            st.error("❌ Debe ingresar el nombre del responsable.")
            return

        # DUI
        if not dui_input.isdigit() or len(dui_input) != 9:
            st.error("❌ El DUI debe tener exactamente 9 dígitos numéricos.")
            return

        dui_formateado = dui_input[:8] + "-" + dui_input[8:]

        # Monto vs saldo
        if monto > saldo:
            st.error(f"❌ No puede gastar ${monto:.2f}. El saldo disponible es de ${saldo:.2f}.")
            return

        # =======================
        # PROCESO DEL GASTO
        # =======================

        # 1. Obtener reunión del día
        id_caja = obtener_o_crear_reunion(fecha)

        # 2. Registrar gasto en tabla Gastos_grupo
        cursor.execute("""
            INSERT INTO Gastos_grupo(Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (fecha, descripcion, monto, responsable, dui_formateado, id_caja))
        con.commit()

        # 3. Registrar movimiento de caja (egreso)
        registrar_movimiento(id_caja, "Egreso", f"Gasto – {descripcion if descripcion else 'Sin concepto'}", monto)

        st.success("✔ Gasto registrado exitosamente.")

        # --------------------------------------------------------
        # GENERAR PDF RESUMEN
        # --------------------------------------------------------
        nombre_pdf = f"gasto_{fecha}_{responsable}.pdf"

        data = [
            ["Campo", "Valor"],
            ["Fecha", fecha],
            ["Responsable", responsable],
            ["DUI", dui_formateado],
            ["Concepto", descripcion if descripcion else "No especificado"],
            ["Monto", f"${monto:.2f}"],
            ["Saldo anterior", f"${saldo:.2f}"],
            ["Saldo después del gasto", f"${saldo - monto:.2f}"],
        ]

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        tabla_pdf = Table(data)

        tabla_pdf.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        doc.build([tabla_pdf])

        with open(nombre_pdf, "rb") as f:
            st.download_button("📥 Descargar PDF del gasto", f, file_name=nombre_pdf)

        st.rerun()

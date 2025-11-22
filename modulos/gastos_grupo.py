import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


def gastos_grupo():

    st.subheader("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # RESPONSABLE
    # --------------------------------------------------------
    responsable = st.text_input("Nombre de la persona responsable del gasto")

    # --------------------------------------------------------
    # DUI (9 dígitos)
    # --------------------------------------------------------
    dui_raw = st.text_input("DUI (9 dígitos)", value="", max_chars=9)

    if len(dui_raw) > 9:
        dui_raw = dui_raw[:9]

    dui_valido = dui_raw.isdigit() and len(dui_raw) == 9

    # --------------------------------------------------------
    # CONCEPTO
    # --------------------------------------------------------
    descripcion = st.text_input("Concepto del gasto (opcional)")

    # --------------------------------------------------------
    # MONTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($)", min_value=0.01, step=0.01)

    # --------------------------------------------------------
    # SALDO DISPONIBLE — SE OBTIENE DIRECTO DESDE caja_reunion
    # --------------------------------------------------------
    cursor.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha <= %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha,))
    row = cursor.fetchone()
    saldo = float(row["saldo_final"]) if row else 0.00

    st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo:.2f}**")

    # --------------------------------------------------------
    # BOTÓN DE REGISTRO
    # --------------------------------------------------------
    if st.button("💳 Registrar gasto"):

        if not dui_valido:
            st.error("❌ El DUI debe tener exactamente 9 dígitos numéricos.")
            return

        if monto > saldo:
            st.error("❌ No se puede registrar el gasto. El saldo es insuficiente.")
            return

        # Obtener o crear la reunión
        id_caja = obtener_o_crear_reunion(fecha)

        try:
            # Registrar gasto
            cursor.execute("""
                INSERT INTO Gastos_grupo (Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha, descripcion, monto, responsable, dui_raw, id_caja))
            con.commit()

            # Registrar egreso en caja
            registrar_movimiento(
                id_caja=id_caja,
                tipo="Egreso",
                categoria=f"Gasto – {descripcion}",
                monto=monto
            )

            st.success("✔ Gasto registrado correctamente.")

            # --------------------------------------------------------
            # GENERAR PDF
            # --------------------------------------------------------
            nombre_pdf = f"gasto_{id_caja}_{fecha}.pdf"

            datos = [
                ["Campo", "Valor"],
                ["Fecha del gasto", fecha],
                ["Responsable", responsable],
                ["DUI", dui_raw],
                ["Monto", f"${monto:.2f}"],
                ["Concepto", descripcion if descripcion else "Sin concepto"],
                ["ID Caja", str(id_caja)]
            ]

            doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
            tabla = Table(datos, colWidths=[150, 300])

            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))

            doc.build([tabla])

            with open(nombre_pdf, "rb") as f:
                st.download_button(
                    label="📄 Descargar PDF del gasto",
                    data=f,
                    file_name=nombre_pdf,
                    mime="application/pdf"
                )

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error registrando el gasto en MySQL.\n\n{e}")

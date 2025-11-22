import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def gastos_grupo():

    st.subheader("💸 Registrar gastos del grupo")

    # Fecha del gasto
    fecha = st.date_input("Fecha del gasto", value=date.today())

    # Responsable
    responsable = st.text_input("Nombre de la persona responsable del gasto")

    # DUI VALIDADO (9 dígitos exactos)
    dui = st.text_input("DUI (9 dígitos)")

    # Concepto opcional
    descripcion = st.text_input("Concepto del gasto (opcional)")

    # Monto
    monto = st.number_input("Monto del gasto ($)", min_value=0.01, step=0.50)

    # ---------------------------------------------------------
    # 📌 Obtener la reunión del día (SE CREA AUTOMÁTICAMENTE)
    # ---------------------------------------------------------
    id_caja = obtener_o_crear_reunion(str(fecha))

    # Obtener saldo actual
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT saldo_final FROM caja_reunion WHERE id_caja = %s", (id_caja,))
    saldo = cursor.fetchone()["saldo_final"]

    st.info(f"💰 Saldo disponible en caja para {fecha}: ${saldo:,.2f}")

    # ---------------------------------------------------------
    # BOTÓN
    # ---------------------------------------------------------
    if st.button("🧾 Registrar gasto"):

        # VALIDACIÓN DUI (solo si NO tiene 9 dígitos)
        if len(dui) != 9 or not dui.isdigit():
            st.error("❌ Debe ingresar un DUI válido de 9 dígitos.")
            return

        # VALIDAR SALDO ANTES DE REGISTRAR
        if monto > saldo:
            st.error("❌ No puede registrar este gasto. El monto excede el saldo disponible en caja.")
            return

        # -----------------------------------------------------
        # REGISTRAR GASTO EN BD
        # -----------------------------------------------------
        try:
            cursor.execute("""
                INSERT INTO Gastos_grupo(Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha, descripcion, monto, responsable, dui, id_caja))
            con.commit()

            # Registrar movimiento en caja (EGRESO)
            registrar_movimiento(id_caja, "Egreso", "Gasto del grupo", monto)

            # Actualizar saldo en caja_reunion
            cursor.execute("""
                UPDATE caja_reunion
                SET egresos = egresos + %s,
                    saldo_final = saldo_final - %s
                WHERE id_caja = %s
            """, (monto, monto, id_caja))
            con.commit()

            st.success("✅ Gasto registrado correctamente.")

        except Exception as e:
            st.error(f"❌ Error al registrar el gasto: {e}")
            return

        # -----------------------------------------------------
        # GENERAR PDF
        # -----------------------------------------------------
        try:
            archivo_pdf = f"gasto_{id_caja}.pdf"
            doc = SimpleDocTemplate(archivo_pdf)
            styles = getSampleStyleSheet()
            contenido = [
                Paragraph("<b>Resumen del Gasto</b>", styles["Title"]),
                Paragraph(f"Fecha: {fecha}", styles["Normal"]),
                Paragraph(f"Responsable: {responsable}", styles["Normal"]),
                Paragraph(f"DUI: {dui}", styles["Normal"]),
                Paragraph(f"Descripción: {descripcion}", styles["Normal"]),
                Paragraph(f"Monto: ${monto:,.2f}", styles["Normal"]),
                Paragraph(f"Saldo previo: ${saldo:,.2f}", styles["Normal"]),
                Paragraph(f"Saldo final: ${(saldo - monto):,.2f}", styles["Normal"]),
            ]
            doc.build(contenido)

            with open(archivo_pdf, "rb") as f:
                st.download_button(
                    label="📄 Descargar comprobante PDF",
                    data=f,
                    file_name=archivo_pdf,
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"⚠ No se pudo generar el PDF: {e}")

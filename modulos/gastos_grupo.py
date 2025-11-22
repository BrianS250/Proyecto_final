import streamlit as st
from datetime import date
from modulos.config.conexion import obtener_conexion
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import tempfile


# -----------------------------------------------------------
# Función principal
# -----------------------------------------------------------
def gastos_grupo():

    st.subheader("💸 Registro de Gastos del Grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    hoy = date.today()

    # -----------------------------------------------------------
    # OBTENER REUNIÓN ACTUAL
    # -----------------------------------------------------------
    cursor.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (hoy,))
    reunion = cursor.fetchone()

    if not reunion:
        st.error("❌ No existe una reunión creada para hoy.")
        return

    id_caja = reunion["id_caja"]
    saldo_disponible = float(reunion["saldo_final"])

    # -----------------------------------------------------------
    # FORMULARIO
    # -----------------------------------------------------------

    responsable = st.text_input("👤 Nombre del responsable del gasto")

    # DUI — SOLO 9 DÍGITOS NUMÉRICOS
    dui = st.text_input("DUI (9 dígitos)", max_chars=9)

    # VALIDACIÓN DUI
    if dui:
        if not dui.isdigit():
            st.error("❌ El DUI solo debe contener números.")
            return

        if len(dui) < 9:
            st.error("❌ Debe ingresar un DUI válido de 9 dígitos.")
            return

    descripcion = st.text_input("Concepto del gasto (opcional)")
    monto = st.number_input("Monto del gasto ($)", min_value=0.01, step=0.50)

    st.info(f"💰 Saldo disponible en caja: **${saldo_disponible:.2f}**")

    if st.button("💾 Registrar gasto"):

        # Validar campos obligatorios
        if responsable.strip() == "":
            st.error("❌ El nombre del responsable es obligatorio.")
            return

        if dui.strip() == "":
            st.error("❌ El DUI es obligatorio.")
            return

        if monto <= 0:
            st.error("❌ El monto debe ser mayor que cero.")
            return

        if monto > saldo_disponible:
            st.error(
                f"❌ No se puede registrar el gasto porque excede el saldo disponible (${saldo_disponible:.2f})."
            )
            return

        # -----------------------------------------------------------
        # REGISTRAR GASTO EN BD
        # -----------------------------------------------------------
        try:
            cursor.execute(
                """
                INSERT INTO Gastos_grupo (Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (hoy, descripcion, monto, responsable, dui, id_caja),
            )

            # REGISTRAR MOVIMIENTO
            cursor.execute(
                """
                INSERT INTO caja_movimientos (id_caja, tipo, categoria, monto)
                VALUES (%s, 'Egreso', 'Gasto del grupo', %s)
                """,
                (id_caja, monto),
            )

            # ACTUALIZAR SALDO EN caja_reunion
            nuevo_saldo = saldo_disponible - monto

            cursor.execute(
                """
                UPDATE caja_reunion
                SET egresos = egresos + %s,
                    saldo_final = %s
                WHERE id_caja = %s
                """,
                (monto, nuevo_saldo, id_caja),
            )

            con.commit()

            st.success("✅ Gasto registrado y saldo actualizado correctamente.")

            # -----------------------------------------------------------
            # GENERAR PDF
            # -----------------------------------------------------------

            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            doc = SimpleDocTemplate(temp.name, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph("<b>Resumen del Gasto del Grupo</b>", styles["Title"]))
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"<b>Fecha:</b> {hoy}", styles["Normal"]))
            story.append(Paragraph(f"<b>Responsable:</b> {responsable}", styles["Normal"]))
            story.append(Paragraph(f"<b>DUI:</b> {dui}", styles["Normal"]))
            story.append(Paragraph(f"<b>Descripción:</b> {descripcion}", styles["Normal"]))
            story.append(Paragraph(f"<b>Monto:</b> ${monto:.2f}", styles["Normal"]))
            story.append(Paragraph(f"<b>Saldo previo:</b> ${saldo_disponible:.2f}", styles["Normal"]))
            story.append(Paragraph(f"<b>Saldo actual:</b> ${nuevo_saldo:.2f}", styles["Normal"]))

            doc.build(story)

            with open(temp.name, "rb") as pdf_file:
                st.download_button(
                    label="📄 Descargar PDF del resumen",
                    data=pdf_file,
                    file_name=f"Resumen_gasto_{hoy}.pdf",
                    mime="application/pdf",
                )

        except Exception as e:
            st.error(f"❌ Error registrando el gasto: {e}")
            con.rollback()

    cursor.close()
    con.close()

import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_por_fecha


# =========================================================
#     MÓDULO COMPLETO — GASTOS DEL GRUPO
# =========================================================
def gastos_grupo():

    st.subheader("🧾 Registrar gastos del grupo")

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
    responsable = st.text_input("Nombre de la persona responsable del gasto")

    # --------------------------------------------------------
    # DUI — VALIDACIÓN REAL
    # --------------------------------------------------------
    dui_raw = st.text_input("DUI (9 dígitos)", value="", max_chars=20)

    # limpiar caracteres no numéricos
    dui_clean = "".join([c for c in dui_raw if c.isdigit()])

    # si el usuario mete más de 9 → recortamos automático
    if len(dui_clean) > 9:
        dui_clean = dui_clean[:9]

    # mostrarlo de vuelta en el campo visible SOLO si cambió
    if dui_raw != dui_clean:
        st.session_state["dui_temp"] = dui_clean

    dui_mostrar = st.text_input(
        "DUI normalizado",
        value=st.session_state.get("dui_temp", dui_clean),
        max_chars=20
    )
    dui_clean = dui_mostrar

    # validación
    if len(dui_clean) == 0:
        st.warning("⚠ Debe ingresar el DUI.")
        dui_valido = False
    elif len(dui_clean) != 9:
        st.error("❌ El DUI debe tener exactamente 9 dígitos.")
        dui_valido = False
    else:
        dui_valido = True

    # --------------------------------------------------------
    # DESCRIPCIÓN (OPCIONAL)
    # --------------------------------------------------------
    descripcion = st.text_input("Concepto del gasto (opcional)")

    # --------------------------------------------------------
    # MONTO
    # --------------------------------------------------------
    monto = st.number_input("Monto del gasto ($)", min_value=0.01, step=0.01)

    # --------------------------------------------------------
    # SALDO DISPONIBLE
    # --------------------------------------------------------
    saldo = obtener_saldo_por_fecha(fecha)
    st.info(f"💰 Saldo disponible en caja para {fecha}: ${saldo:.2f}")

    # --------------------------------------------------------
    # BOTÓN
    # --------------------------------------------------------
    if st.button("💳 Registrar gasto"):

        # DUI inválido → cancelar
        if not dui_valido:
            return

        # monto mayor al saldo → cancelar
        if monto > saldo:
            st.error("❌ No se puede registrar este gasto porque excede el saldo disponible.")
            return

        # obtener o crear reunión automáticamente (OPCIÓN A)
        id_caja = obtener_o_crear_reunion(fecha)

        # registrar gasto en DB
        try:
            cursor.execute("""
                INSERT INTO Gastos_grupo(Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fecha, descripcion, monto, responsable, dui_clean, id_caja))
            con.commit()
        except Exception as e:
            st.error(f"❌ Error registrando el gasto en MySQL.\n\n{e}")
            return

        # registrar movimiento en caja
        registrar_movimiento(id_caja, "Egreso", f"Gasto – {descripcion}", monto)

        st.success("✔ Gasto registrado correctamente.")

        # --------------------------------------------------------
        # PDF
        # --------------------------------------------------------
        try:
            styles = getSampleStyleSheet()
            pdf_path = f"reporte_gasto_{fecha}.pdf"
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)

            story = []
            story.append(Paragraph("<b>Reporte de Gasto del Grupo</b>", styles["Title"]))
            story.append(Paragraph(f"Fecha: {fecha}", styles["Normal"]))
            story.append(Paragraph(f"Responsable: {responsable}", styles["Normal"]))
            story.append(Paragraph(f"DUI: {dui_clean}", styles["Normal"]))
            story.append(Paragraph(f"Concepto: {descripcion}", styles["Normal"]))
            story.append(Paragraph(f"Monto: ${monto:.2f}", styles["Normal"]))
            story.append(Paragraph(f"Nuevo saldo en caja: ${saldo - monto:.2f}", styles["Normal"]))

            doc.build(story)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📄 Descargar PDF del gasto",
                    data=f,
                    file_name=pdf_path,
                    mime="application/pdf"
                )

        except Exception as e:
            st.warning(f"⚠ No se pudo generar el PDF correctamente.\n\n{e}")

        st.rerun()

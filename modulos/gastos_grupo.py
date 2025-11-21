import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion

# Caja por reunión
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch


def gastos_grupo():

    st.header("🧾 Registro de otros gastos del grupo")

    # -----------------------------
    # FORMULARIO
    # -----------------------------
    fecha_raw = st.date_input("📅 Fecha del gasto", date.today())
    fecha_gasto = fecha_raw.strftime("%Y-%m-%d")

    concepto = st.text_input("📝 Concepto del gasto (ej. 'Refrigerio', 'Materiales')")
    responsable = st.text_input("👤 Responsable del gasto (opcional)")
    monto = st.number_input("💵 Monto del gasto ($)", min_value=0.25, step=0.25)

    if st.button("➖ Registrar gasto"):

        if concepto.strip() == "":
            st.warning("⚠ Debe escribir un concepto del gasto.")
            return

        try:
            # 1️⃣ Crear/obtener reunión
            id_caja = obtener_o_crear_reunion(fecha_gasto)

            # 2️⃣ Registrar movimiento (EGRESO)
            descripcion = f"Gasto del grupo – {concepto}"
            if responsable.strip() != "":
                descripcion += f" (Responsable: {responsable})"

            registrar_movimiento(
                id_caja,
                "Egreso",
                descripcion,
                monto
            )

            st.success("✔ Gasto registrado y descontado de la caja del día.")

            # Guardamos datos para mostrar el resumen
            st.session_state["ultimo_gasto"] = {
                "fecha": fecha_gasto,
                "concepto": concepto,
                "responsable": responsable if responsable else "No especificado",
                "monto": monto
            }

        except Exception as e:
            st.error(f"❌ Error al registrar gasto: {e}")


    # ======================================================
    # MOSTRAR RESUMEN SI EXISTE UN GASTO RECIENTE
    # ======================================================
    if "ultimo_gasto" in st.session_state:

        data = st.session_state["ultimo_gasto"]

        st.markdown("---")
        st.subheader("📄 Resumen del gasto registrado")

        st.write(f"**📅 Fecha:** {data['fecha']}")
        st.write(f"**📝 Concepto:** {data['concepto']}")
        st.write(f"**👤 Responsable:** {data['responsable']}")
        st.write(f"**💵 Monto:** ${data['monto']:.2f}")

        # ======================================================
        # BOTÓN PARA PDF
        # ======================================================
        if st.button("📥 Descargar PDF del gasto"):

            nombre_pdf = f"gasto_{data['fecha']}.pdf"
            doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)

            tabla_data = [
                ["Campo", "Valor"],
                ["Fecha del gasto", data["fecha"]],
                ["Concepto", data["concepto"]],
                ["Responsable", data["responsable"]],
                ["Monto ($)", f"${data['monto']:.2f}"]
            ]

            tabla = Table(tabla_data)
            tabla.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("ALIGN", (0,0), (-1,-1), "CENTER"),
                ("BOX", (0,0), (-1,-1), 1, colors.black),
                ("GRID", (0,0), (-1,-1), 1, colors.black),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("FONTSIZE", (0,0), (-1,-1), 11),
                ("BOTTOMPADDING", (0,0), (-1,0), 10),
            ]))

            doc.build([tabla])

            with open(nombre_pdf, "rb") as f:
                st.download_button(
                    "📄 Descargar PDF",
                    f,
                    file_name=nombre_pdf,
                    mime="application/pdf"
                )

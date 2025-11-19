import streamlit as st
from modulos.conexion import obtener_conexion
from datetime import date
import pandas as pd

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import base64
import io


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor()

    # ======================================================
    # OBTENER SOCIAS
    # ======================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {nombre: ids for (ids, nombre) in socias}

    # ======================================================
    # FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today())

        nombre_socia = st.selectbox("👩 Socia que recibe el préstamo", list(lista_socias.keys()))
        id_socia = lista_socias[nombre_socia]

        proposito = st.text_input("🎯 Propósito del préstamo (opcional)")

        monto = st.number_input("💵 Monto solicitado", min_value=1, step=1)

        tasa_interes = st.number_input("📈 Tasa de interés (%)", min_value=1, value=10)

        plazo = st.number_input("🗓 Plazo (meses)", min_value=1)
        cuotas = st.number_input("📑 Número de cuotas (puede ser distinto del plazo)", min_value=1)

        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    # ======================================================
    # PROCESAR FORMULARIO
    # ======================================================
    if enviar:

        # --------------------------------------------------
        # 1. VERIFICAR SALDO DE CAJA
        # --------------------------------------------------
        cursor.execute("SELECT Id_Caja, Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
        caja = cursor.fetchone()

        if not caja:
            st.error("❌ No existe caja activa.")
            return

        id_caja, saldo_actual = caja

        if monto > saldo_actual:
            st.error(f"❌ Fondos insuficientes. Saldo disponible: ${saldo_actual}")
            return

        saldo_pendiente = monto

        try:
            # --------------------------------------------------
            # 2. REGISTRAR PRÉSTAMO
            # --------------------------------------------------
            cursor.execute("""
                INSERT INTO Prestamo(
                    `Fecha del préstamo`,
                    `Monto prestado`,
                    `Tasa de interes`,
                    `Plazo`,
                    `Cuotas`,
                    `Saldo pendiente`,
                    `Estado del préstamo`,
                    Id_Socia,
                    Id_Caja
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                fecha_prestamo,
                monto,
                tasa_interes,
                plazo,
                cuotas,
                saldo_pendiente,
                "activo",
                id_socia,
                id_caja
            ))

            # --------------------------------------------------
            # 3. REGISTRAR EGRESO EN CAJA
            # --------------------------------------------------
            cursor.execute("""
                INSERT INTO Caja(Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento)
                VALUES (%s,%s,%s,%s,%s)
            """,
            (
                f"Préstamo otorgado a: {nombre_socia}",
                -monto,
                saldo_actual - monto,
                1,
                3
            ))

            nuevo_saldo = saldo_actual - monto
            con.commit()

            st.success("✔ Préstamo autorizado correctamente.")
            st.info(f"Nuevo saldo en caja: ${nuevo_saldo}")

        except Exception as e:
            st.error(f"❌ Error al registrar el préstamo: {e}")
            return

        # =====================================================
        # 📘 RESUMEN DEL PRÉSTAMO
        # =====================================================

        interes_total = monto * (tasa_interes / 100)
        total_pagar = monto + interes_total
        pago_por_cuota = total_pagar / cuotas

        st.markdown("---")
        st.markdown("## 📘 Detalle del préstamo")

        tabla_resumen = {
            "Campo": [
                "ID Socia", "Nombre", "Monto prestado", "Tasa de interés",
                "Plazo (meses)", "Cuotas", "Interés total",
                "Total a pagar", "Pago por cuota", "Fecha del préstamo"
            ],
            "Valor": [
                id_socia,
                nombre_socia,
                f"${monto:.2f}",
                f"{tasa_interes}%",
                plazo,
                cuotas,
                f"${interes_total:.2f}",
                f"${total_pagar:.2f}",
                f"${pago_por_cuota:.2f}",
                str(fecha_prestamo)
            ]
        }

        df_resumen = pd.DataFrame(tabla_resumen)
        st.table(df_resumen)

        # =====================================================
        # 📄 GENERAR PDF
        # =====================================================
        def generar_pdf():
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elementos = []

            estilos = getSampleStyleSheet()
            titulo = Paragraph("Resumen del Préstamo", estilos["Title"])
            elementos.append(titulo)
            elementos.append(Spacer(1, 12))

            data = [["Campo", "Valor"]]
            for i in range(len(tabla_resumen["Campo"])):
                data.append([tabla_resumen["Campo"][i], tabla_resumen["Valor"][i]])

            tabla_pdf = Table(data, colWidths=[150, 300])
            tabla_pdf.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E86C1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#EAF2F8")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.gray),
            ]))

            elementos.append(tabla_pdf)
            doc.build(elementos)

            pdf = buffer.getvalue()
            buffer.close()

            b64 = base64.b64encode(pdf).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="Prestamo_{id_socia}.pdf">📄 Descargar PDF del préstamo</a>'
            return href

        st.markdown("### 📄 Exportar")
        st.markdown(generar_pdf(), unsafe_allow_html=True)

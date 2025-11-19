import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import io


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor()

    # ======================================================
    # OBTENER SOCIAS
    # ======================================================
   cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
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
        cuotas = st.number_input("📑 Número de cuotas", min_value=1)

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

        # --------------------------------------------------
        # 2. CÁLCULOS DEL PRÉSTAMO
        # --------------------------------------------------
        interes_total = monto * (tasa_interes/100)
        total_pagar = monto + interes_total
        cuota_final = total_pagar / cuotas

        saldo_pendiente = monto

        # --------------------------------------------------
        # 3. REGISTRAR PRÉSTAMO
        # --------------------------------------------------
        try:
            cursor.execute("""
                INSERT INTO Prestamo(
                    `Fecha del préstamo`,
                    `Monto prestado`,
                    `Tasa de interes`,
                    `Plazo`,
                    `Cuotas`,
                    `Saldo pendiente`,
                    `Estado del préstamo`,
                    Id_Grupo,
                    Id_Socia,
                    Id_Caja
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                fecha_prestamo,
                monto,
                tasa_interes,
                plazo,
                cuotas,
                saldo_pendiente,
                "activo",
                1,          # Id_Grupo
                id_socia,   # Id de la socia
                id_caja     # Id de caja
            ))

            # --------------------------------------------------
            # 4. REGISTRAR EGRESO EN CAJA
            # --------------------------------------------------
            cursor.execute("""
                INSERT INTO Caja(Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento)
                VALUES (%s,%s,%s,%s,%s)
            """,
            (
                f"Préstamo otorgado a: {nombre_socia}",
                -monto,
                saldo_actual - monto,
                1,      # Id_Grupo
                3       # 3 = Egreso
            ))

            con.commit()

        except Exception as e:
            st.error(f"❌ Error al registrar el préstamo: {e}")
            return

        # --------------------------------------------------
        # 5. MENSAJE DE ÉXITO
        # --------------------------------------------------
        st.success("✅ Préstamo autorizado correctamente.")
        st.info(f"Nuevo saldo en caja: ${saldo_actual - monto}")

        # --------------------------------------------------
        # 6. RESUMEN DEL PRÉSTAMO EN TABLA
        # --------------------------------------------------
        st.markdown("## 📄 Resumen del préstamo autorizado")

        resumen_df = pd.DataFrame({
            "Descripción": [
                "ID de la socia",
                "Nombre de la socia",
                "Monto prestado",
                "Tasa de interés",
                "Plazo (meses)",
                "Número de cuotas",
                "Interés total",
                "Total a pagar",
                "Pago por cuota",
                "Fecha del préstamo"
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
                f"${cuota_final:.2f}",
                fecha_prestamo
            ]
        })

        st.table(resumen_df)

        # --------------------------------------------------
        # 7. GENERAR PDF
        # --------------------------------------------------
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(1 * inch, 10.5 * inch, "Resumen del préstamo autorizado")

        pdf.setFont("Helvetica", 12)
        y = 10 * inch

        for desc, val in zip(resumen_df["Descripción"], resumen_df["Valor"]):
            pdf.drawString(1 * inch, y, f"{desc}:  {val}")
            y -= 0.3 * inch

        pdf.save()
        buffer.seek(0)

        st.download_button(
            label="📥 Descargar resumen en PDF",
            data=buffer,
            file_name="resumen_prestamo.pdf",
            mime="application/pdf"
        )

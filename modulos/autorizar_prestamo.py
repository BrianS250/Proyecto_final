import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

# NUEVAS FUNCIONES DE CAJA POR REUNIÓN (OPCIÓN A)
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


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

    lista_socias = {f"{id} - {nombre}": id for (id, nombre) in socias}

    # ======================================================
    # FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_prestamo_raw = st.date_input("📅 Fecha del préstamo", date.today())
        fecha_prestamo = fecha_prestamo_raw.strftime("%Y-%m-%d")

        socia_seleccionada = st.selectbox("👩 Socia que recibe el préstamo", list(lista_socias.keys()))
        id_socia = lista_socias[socia_seleccionada]

        monto = st.number_input("💵 Monto prestado ($):", min_value=1, step=1)
        tasa_interes = st.number_input("📈 Tasa de interés (%):", min_value=1, step=1)
        plazo = st.number_input("🗓 Plazo (meses):", min_value=1)
        cuotas = st.number_input("📑 Número de cuotas:", min_value=1)

        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    # ======================================================
    # PROCESAR FORMULARIO
    # ======================================================
    if enviar:

        # ======================================================
        # VERIFICAR AHORRO DE LA SOCIA
        # ======================================================
        cursor.execute("""
            SELECT `Saldo acumulado`
            FROM Ahorro
            WHERE Id_Socia = %s
            ORDER BY Id_Ahorro DESC
            LIMIT 1
        """, (id_socia,))

        row_ahorro = cursor.fetchone()
        saldo_ahorro = row_ahorro[0] if row_ahorro else 0

        if monto > saldo_ahorro:
            st.error(f"""
            ❌ No es posible autorizar este préstamo.

            La socia tiene en ahorros: **${saldo_ahorro:.2f}**  
            Monto solicitado: **${monto:.2f}**

            🔒 *El monto del préstamo no puede ser mayor que el ahorro disponible.*
            """)
            return

        # ======================================================
        # VERIFICAR FONDOS DE CAJA (OPCIÓN A)
        # ======================================================
        cursor.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
        row_caja = cursor.fetchone()
        saldo_actual_caja = row_caja[0] if row_caja else 0

        if monto > saldo_actual_caja:
            st.error(f"❌ Fondos insuficientes en caja. Saldo disponible: ${saldo_actual_caja}")
            return

        saldo_pendiente = monto

        try:
            # --------------------------------------------------
            # 1. REGISTRAR PRÉSTAMO EN TABLA Prestamo
            # --------------------------------------------------
            cursor.execute("""
                INSERT INTO Prestamo(
                    `Fecha del préstamo`,
                    `Monto prestado`,
                    `Tasa de interes`,
                    `Plazo`,
                    `Cuotas`,
                    `Saldo pendiente`,
                    Estado_del_prestamo,
                    Id_Grupo,
                    Id_Socia
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
                1,
                id_socia
            ))

            con.commit()

            # --------------------------------------------------
            # 2. REGISTRAR EGRESO EN CAJA POR REUNIÓN
            # --------------------------------------------------
            id_caja_reunion = obtener_o_crear_reunion(fecha_prestamo)

            registrar_movimiento(
                id_caja_reunion,
                "Egreso",
                f"Préstamo otorgado a: {socia_seleccionada}",
                float(monto)
            )

            # --------------------------------------------------
            # 3. MOSTRAR RESUMEN
            # --------------------------------------------------
            interes_total = monto * (tasa_interes / 100)
            total_a_pagar = monto + interes_total
            pago_por_cuota = total_a_pagar / cuotas

            st.success("✔ Préstamo autorizado correctamente.")

            st.subheader("📄 Resumen del préstamo autorizado")

            data = [
                ["Campo", "Valor"],
                ["ID de socia", id_socia],
                ["Nombre", socia_seleccionada.split(" - ")[1]],
                ["Monto prestado", f"${monto:.2f}"],
                ["Interés (%)", f"{tasa_interes}%"],
                ["Interés total generado", f"${interes_total:.2f}"],
                ["Total a pagar", f"${total_a_pagar:.2f}"],
                ["Cuotas", cuotas],
                ["Pago por cuota", f"${pago_por_cuota:.2f}"],
                ["Fecha del préstamo", fecha_prestamo],
                ["Saldo en ahorros", f"${saldo_ahorro:.2f}"]
            ]

            df_resumen = pd.DataFrame(data, columns=["Detalle", "Valor"])
            st.table(df_resumen)

            # ======================================================
            # 4. DESCARGAR PDF
            # ======================================================
            if st.button("📥 Descargar resumen en PDF"):

                nombre_pdf = f"prestamo_socia_{id_socia}.pdf"

                doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
                tabla_pdf = Table(data)
                tabla_pdf.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), colors.gray),
                    ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                    ("ALIGN", (0,0), (-1,-1), "CENTER"),
                    ("BOX", (0,0), (-1,-1), 1, colors.black),
                    ("GRID", (0,0), (-1,-1), 1, colors.black),
                ]))

                doc.build([tabla_pdf])

                with open(nombre_pdf, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name=nombre_pdf)

        except Exception as e:
            st.error(f"❌ Error al registrar el préstamo: {e}")

        finally:
            cursor.close()
            con.close()

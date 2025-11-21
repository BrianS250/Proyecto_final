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
    # DUI
    # --------------------------------------------------------
    dui_input = st.text_area(
        "DUI (9 dígitos)",
        height=40,
        max_chars=9
    ).strip()

    # --------------------------------------------------------
    # CONCEPTO (OPCIONAL)
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
    # BOTÓN PRINCIPAL
    # --------------------------------------------------------
    if st.button("💳 Registrar gasto"):

        # ======================================================
        # 1. VALIDAR MONTO
        # ======================================================
        if monto > saldo:
            st.error(f"❌ No puede gastar ${monto:.2f}. Saldo disponible: ${saldo:.2f}")
            return

        # ======================================================
        # 2. VALIDAR RESPONSABLE
        # ======================================================
        if not responsable.strip():
            st.error("❌ Debe ingresar el nombre del responsable.")
            return

        # ======================================================
        # 3. VALIDAR DUI
        # ======================================================
        dui_limpio = dui_input.replace("-", "")

        if not dui_limpio.isdigit() or len(dui_limpio) != 9:
            st.error("❌ El DUI debe tener exactamente 9 dígitos numéricos.")
            return

        dui_formateado = dui_limpio[:8] + "-" + dui_limpio[8:]

        # ======================================================
        # 4. OBTENER CAJA (GARANTIZADO)
        # ======================================================
        id_caja = obtener_o_crear_reunion(fecha)

        # FORZAR A TIPO INT
        try:
            id_caja = int(id_caja)
        except:
            st.error("❌ Error interno: Id_Caja inválido.")
            return

        # ======================================================
        # 5. REGISTRAR GASTO (A PRUEBA DE ERRORES)
        # ======================================================
        try:
            cursor.execute("""
                INSERT INTO Gastos_grupo(Fecha_gasto, Descripcion, Monto, Responsable, DUI, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                fecha,
                descripcion if descripcion.strip() else "Sin concepto",
                monto,
                responsable,
                dui_formateado,
                id_caja
            ))
            con.commit()

        except Exception as e:
            st.error("❌ Error registrando el gasto en MySQL.")
            st.error(str(e))
            return

        # ======================================================
        # 6. REGISTRAR MOVIMIENTO EN CAJA
        # ======================================================
        registrar_movimiento(
            id_caja,
            "Egreso",
            f"Gasto – {descripcion if descripcion.strip() else 'Sin concepto'}",
            monto
        )

        st.success("✔ Gasto registrado exitosamente.")

        # ======================================================
        # 7. GENERAR PDF
        # ======================================================
        nombre_pdf = f"gasto_{fecha}_{responsable}.pdf"

        data = [
            ["Campo", "Valor"],
            ["Fecha", fecha],
            ["Responsable", responsable],
            ["DUI", dui_formateado],
            ["Concepto", descripcion if descripcion.strip() else "Sin concepto"],
            ["Monto del gasto", f"${monto:.2f}"],
            ["Saldo antes", f"${saldo:.2f}"],
            ["Saldo después", f"${saldo - monto:.2f}"],
        ]

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        tabla = Table(data)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        doc.build([tabla])

        with open(nombre_pdf, "rb") as f:
            st.download_button("📥 Descargar PDF del gasto", f, file_name=nombre_pdf)

        st.rerun()

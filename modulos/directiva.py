import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion

# MÓDULOS EXTERNOS
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.reporte_caja import reporte_caja
from modulos.gastos_grupo import gastos_grupo
from modulos.cierre_ciclo import cierre_ciclo
from modulos.reglas import gestionar_reglas

# CAJA
from modulos.caja import (
    obtener_o_crear_reunion,
    registrar_movimiento,
    obtener_saldo_actual,
    obtener_reporte_reunion
)

# PARA REGLAS INTERNAS
from modulos.reglas_utils import obtener_reglas



# ============================================================
# PANEL PRINCIPAL — DIRECTIVA
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    # ------------------------------------------
    # VALIDAR ROL
    # ------------------------------------------
    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    # ------------------------------------------
    # CERRAR SESIÓN
    # ------------------------------------------
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.session_state["rol"] = None
        st.rerun()

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # ============================================================
    # FECHA GLOBAL PARA REPORTES
    # ============================================================
    if "fecha_global" not in st.session_state:
        st.session_state["fecha_global"] = date.today().strftime("%Y-%m-%d")

    fecha_sel = st.date_input(
        "📅 Fecha del reporte",
        value=pd.to_datetime(st.session_state["fecha_global"]),
    ).strftime("%Y-%m-%d")

    st.session_state["fecha_global"] = fecha_sel

    # ============================================================
    # SALDO ACTUAL
    # ============================================================
    try:
        saldo_global = obtener_saldo_actual()
        st.success(f"💰 Saldo REAL en caja: **${saldo_global:.2f}**")
    except:
        st.error("⚠ No se pudo obtener el saldo actual de caja.")

    # ============================================================
    # REPORTE DEL DÍA
    # ============================================================
    try:
        reporte = obtener_reporte_reunion(fecha_sel)

        ingresos = reporte["ingresos"]
        egresos = reporte["egresos"]
        balance = reporte["balance"]
        saldo_final = reporte["saldo_final"]

        st.subheader(f"📊 Reporte del día {fecha_sel}")

        st.info(
            f"""
            📥 **Ingresos del día:** ${ingresos:.2f}  
            📤 **Egresos del día:** ${egresos:.2f}  
            📘 **Balance del día:** ${balance:.2f}  
            🔚 **Saldo final registrado ese día:** ${saldo_final:.2f}
            """
        )

    except Exception as e:
        st.error(f"⚠ Error al generar reporte diario: {str(e)}")

    st.write("---")

    # ============================================================
    # MENÚ LATERAL
    # ============================================================
    menu = st.sidebar.radio(
        "Menú rápido:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro",
            "Registrar otros gastos",
            "Cierre de ciclo",
            "Reporte de caja",
            "Reglas internas"
        ]
    )

    # ============================================================
    # SECCIONES DEL MENÚ
    # ============================================================
    if menu == "Registro de asistencia":
        from modulos.directiva_asistencia import pagina_asistencia
        pagina_asistencia()

    elif menu == "Aplicar multas":
        from modulos.directiva_multas import pagina_multas
        pagina_multas()

    elif menu == "Registrar nuevas socias":
        from modulos.directiva_socias import pagina_registro_socias
        pagina_registro_socias()

    elif menu == "Autorizar préstamo":
        autorizar_prestamo()

    elif menu == "Registrar pago de préstamo":
        pago_prestamo()

    elif menu == "Registrar ahorro":
        ahorro()

    elif menu == "Registrar otros gastos":
        gastos_grupo()

    elif menu == "Cierre de ciclo":
        cierre_ciclo()

    elif menu == "Reporte de caja":
        reporte_caja()

    elif menu == "Reglas internas":
        gestionar_reglas()


    # ============================================================
    # RESUMEN DEL CICLO (USANDO REGLAS INTERNAS)
    # ============================================================
    reglas = obtener_reglas()

    if reglas:
        fecha_inicio_ciclo = reglas.get("ciclo_inicio")

        if fecha_inicio_ciclo:
            st.markdown("---")
            st.subheader("📊 Resumen del ciclo actual")

            con = obtener_conexion()
            cur = con.cursor(dictionary=True)

            cur.execute("""
                SELECT 
                    IFNULL(SUM(ingresos),0) AS total_ingresos,
                    IFNULL(SUM(egresos),0) AS total_egresos
                FROM caja_reunion
                WHERE fecha >= %s
            """, (fecha_inicio_ciclo,))

            tot = cur.fetchone()

            total_ingresos_ciclo = float(tot["total_ingresos"])
            total_egresos_ciclo = float(tot["total_egresos"])
            balance = total_ingresos_ciclo - total_egresos_ciclo

            st.write(f"📥 **Ingresos acumulados del ciclo:** ${total_ingresos_ciclo:.2f}")
            st.write(f"📤 **Egresos acumulados del ciclo:** ${total_egresos_ciclo:.2f}")
            st.write(f"💼 **Balance del ciclo:** ${balance:.2f}")

            cur.close()
            con.close()
        else:
            st.info("⚠ No hay fecha de inicio de ciclo registrada.")

    else:
        st.info("⚠ Debe registrar reglas internas primero.")

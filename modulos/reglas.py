import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

# 👉 Importación del módulo de reglas internas
from modulos.reglas import gestionar_reglas


# ---------------------------------------------------------
# PANEL PRINCIPAL DE LA DIRECTIVA
# ---------------------------------------------------------
def interfaz_directiva():

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # ---------------------------------------------------------
    # MENÚ LATERAL (RADIO)
    # ---------------------------------------------------------
    opcion = st.sidebar.radio(
        "Selección rápida:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro",
            "Registrar otros gastos",
            "Reporte de caja",
            "Reglas internas"   # ← OPCIÓN AGREGADA
        ]
    )

    # ---------------------------------------------------------
    # RUTEO SEGÚN OPCIÓN SELECCIONADA
    # ---------------------------------------------------------

    if opcion == "Registro de asistencia":
        mostrar_asistencias()

    elif opcion == "Aplicar multas":
        aplicar_multas()

    elif opcion == "Registrar nuevas socias":
        registrar_socia()

    elif opcion == "Autorizar préstamo":
        autorizar_prestamo()

    elif opcion == "Registrar pago de préstamo":
        registrar_pago_prestamo()

    elif opcion == "Registrar ahorro":
        registrar_ahorro()

    elif opcion == "Registrar otros gastos":
        registrar_gastos()

    elif opcion == "Reporte de caja":
        reporte_caja()

    # ---------------------------------------------------------
    # OPCIÓN NUEVA
    # ---------------------------------------------------------
    elif opcion == "Reglas internas":
        gestionar_reglas()   # ← Abre el módulo completo


# ---------------------------------------------------------
# FUNCIONES EXISTENTES EN TU SISTEMA
# (NO CAMBIÉ NADA AQUÍ, SOLO MANTUVE TU ESTRUCTURA)
# ---------------------------------------------------------

def mostrar_asistencias():
    st.subheader("Registro de Asistencias")
    st.info("Aquí va tu código actual.")


def aplicar_multas():
    st.subheader("Aplicar Multas")
    st.info("Aquí va tu código actual.")


def registrar_socia():
    st.subheader("Registrar nuevas socias")
    st.info("Aquí va tu código actual.")


def autorizar_prestamo():
    st.subheader("Autorizar préstamo")
    st.info("Aquí va tu código actual.")


def registrar_pago_prestamo():
    st.subheader("Registrar pago de préstamo")
    st.info("Aquí va tu código actual.")


def registrar_ahorro():
    st.subheader("Registrar ahorro")
    st.info("Aquí va tu código actual.")


def registrar_gastos():
    st.subheader("Registrar otros gastos")
    st.info("Aquí va tu código actual.")


def reporte_caja():
    st.subheader("Reporte de caja")
    st.info("Aquí va tu código actual.")

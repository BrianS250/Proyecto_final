import streamlit as st
import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="btfcfbzptdyxq4f8afmu"
    )

def interfaz_promotora():
    st.title("👩‍💼 Panel de Promotora del Grupo")
    st.write("Registra pagos, reuniones y reportes de actividades.")

    opcion = st.sidebar.radio("Selecciona una opción:", [
        "Registrar asistencia",
        "Registrar pago de préstamo",
        "Generar reporte de actividades"
    ])

    if opcion == "Registrar asistencia":
        st.subheader("🗓️ Registro de asistencia")
        nombre = st.text_input("Nombre del miembro")
        fecha = st.date_input("Fecha de asistencia")

        if st.button("Registrar asistencia"):
            if nombre:
                try:
                    con = obtener_conexion()
                    cur = con.cursor()
                    cur.execute("INSERT INTO Asistencia (Id_Asistencia) VALUES (NULL)")
                    con.commit()
                    con.close()
                    st.success(f"✅ Asistencia de {nombre} registrada correctamente.")
                except Exception as e:
                    st.error(f"Error al registrar asistencia: {e}")
            else:
                st.warning("⚠️ Ingresa el nombre del miembro.")

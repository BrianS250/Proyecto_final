import streamlit as st

def interfaz_promotora():
    st.title("👩‍💼 Panel de Promotora")
    st.write("Supervisa tus grupos, registra nuevos y valida información financiera.")

    opciones = [
        "Consultar grupos",
        "Registrar nuevo grupo",
        "Validar información financiera",
        "Reportes consolidados"
    ]

    seleccion = st.sidebar.radio("Selecciona una opción:", opciones)

    if seleccion == "Consultar grupos":
        pagina_consultar_grupos()

    elif seleccion == "Registrar nuevo grupo":
        pagina_registrar_grupo()

    elif seleccion == "Validar información financiera":
        pagina_validar_finanzas()

    elif seleccion == "Reportes consolidados":
        pagina_reportes()


# ======== PÁGINAS ========

def pagina_consultar_grupos():
    st.header("📋 Grupos Asignados")
    st.info("Grupo Mujeres Unidas")
    st.info("Grupo Esperanza")


def pagina_registrar_grupo():
    st.header("📝 Registrar nuevo grupo")
    nombre = st.text_input("Nombre del grupo")
    inicio = st.date_input("Fecha de inicio")
    tasa = st.number_input("Tasa de interés (%)", min_value=0.0, step=0.1)
    periodicidad = st.selectbox("Periodicidad de reuniones", ["Semanal", "Quincenal", "Mensual"])
    if st.button("Registrar grupo"):
        st.success("Grupo registrado correctamente.")


def pagina_validar_finanzas():
    st.header("💵 Validar información financiera")
    st.success("Aquí podrás revisar préstamos, pagos y movimientos.")


def pagina_reportes():
    st.header("📊 Reportes consolidados")
    st.info("Generación de reportes financieros generales.")

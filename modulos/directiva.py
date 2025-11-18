import streamlit as st
from modulos.login import login
from modulos.venta import mostrar_venta
from modulos.administrador import interfaz_administrador
from modulos.promotora import interfaz_promotora
from modulos.asistencia import interfaz_asistencia
from modulos.conexion import obtener_conexion


# ================================
#   INTERFAZ DIRECTIVA
# ================================
def interfaz_directiva():

    # Si no hay sesión, volver al login
    if "sesion_iniciada" not in st.session_state or not st.session_state["sesion_iniciada"]:
        login()
        return

    st.sidebar.title("Menú principal")

    # Mostrar quién inició sesión
    usuario = st.session_state.get("usuario", "Usuario desconocido")
    rol = st.session_state.get("rol", "")
    st.sidebar.success(f"Sesión iniciada como:\n**{usuario} ({rol})**")

    # --------------------------
    # BOTÓN: Cerrar sesión
    # --------------------------
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.session_state["usuario"] = ""
        st.session_state["rol"] = ""
        st.rerun()

    # --------------------------
    # OPCIONES DEL PANEL
    # --------------------------
    opcion = st.sidebar.radio(
        "Seleccione una opción:",
        [
            "Registrar reunión y asistencia",
            "Registrar préstamos o pagos",
            "Aplicar multas",
            "Generar actas y reportes",
        ]
    )

    # Encabezado general
    st.title("👥 Panel de Directiva del Grupo")
    st.write("Aquí puede registrar reuniones, préstamos, multas y generar reportes.")


    # =====================================================================
    # OPCIÓN 1: REGISTRO DE ASISTENCIA
    # =====================================================================
    if opcion == "Registrar reunión y asistencia":
        interfaz_asistencia()


    # =====================================================================
    # OPCIÓN 2: PRÉSTAMOS / PAGOS
    # =====================================================================
    if opcion == "Registrar préstamos o pagos":
        mostrar_venta()


    # =====================================================================
    # OPCIÓN 3: MULTAS
    # =====================================================================
    if opcion == "Aplicar multas":
        pagina_multas()


    # =====================================================================
    # OPCIÓN 4: REPORTES
    # =====================================================================
    if opcion == "Generar actas y reportes":
        st.subheader("📄 Generación de reportes (pendiente)")
        st.info("Aquí podrás generar actas y reportes del grupo.")



# ==================================================
#        MÓDULO DE MULTAS (YA FUNCIONA)
# ==================================================
def pagina_multas():
    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ Error: no se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # Obtener socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()

    lista_socias = {s[1]: s[0] for s in socias}

    # Obtener tipos de multa
    cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_de_multa")
    tipos_multa = cursor.fetchall()

    mapa_tipos = {t[1]: t[0] for t in tipos_multa}

    # ----------------------
    # FORMULARIO DE MULTAS
    # ----------------------
    nombre_socia = st.selectbox("Seleccione la socia:", list(lista_socias.keys()))
    tipo_multa = st.selectbox("Tipo de multa:", list(mapa_tipos.keys()))
    monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.50)
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado", ["A pagar", "Pagado"])

    if st.button("💾 Registrar multa"):
        id_socia = lista_socias[nombre_socia]
        id_tipo = mapa_tipos[tipo_multa]

        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo, id_socia))
            con.commit()

            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error registrando la multa: {e}")

    con.close()

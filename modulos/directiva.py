import streamlit as st
from modulos.conexion import obtener_conexion


# ======================================================
#  PANEL PRINCIPAL DE DIRECTIVA
# ======================================================
def interfaz_directiva():
    st.title("👨‍💼 Panel de Directiva del Grupo")
    st.write("Registrar reuniones, préstamos, multas y generar reportes.")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ]

    seleccion = st.sidebar.radio("Seleccione una opción:", opciones)

    if seleccion == "Registrar reunión y asistencia":
        pagina_reunion()

    elif seleccion == "Registrar préstamos o pagos":
        pagina_prestamos()

    elif seleccion == "Aplicar multas":
        pagina_multas()   # CORREGIDO Y FUNCIONAL

    elif seleccion == "Generar actas y reportes":
        pagina_reportes()



# ======================================================
# 1. REGISTRO DE REUNIONES
# ======================================================
def pagina_reunion():
    st.header("📅 Registro de reunión")
    fecha = st.date_input("Fecha de la reunión")
    tema = st.text_input("Tema principal")
    asistentes = st.text_input("Lista de asistentes (separados por coma)")

    if st.button("Guardar reunión"):
        st.success("Reunión registrada correctamente.")



# ======================================================
# 2. PRÉSTAMOS O PAGOS
# ======================================================
def pagina_prestamos():
    st.header("💰 Registro de préstamos o pagos")
    tipo = st.selectbox("Tipo de registro", ["Préstamo", "Pago"])
    descripcion = st.text_area("Descripción")

    if st.button("Guardar movimiento"):
        st.success("Movimiento registrado correctamente.")



# ======================================================
# 3. FORMULARIO REAL — APLICACIÓN DE MULTAS
# ======================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    # ==========================================
    # Conexión a MySQL
    # ==========================================
    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con MySQL.")
        return

    cursor = con.cursor()

    # ==========================================
    # Cargar SOCIAS desde tabla Socia
    # ==========================================
    try:
        cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
        socias = cursor.fetchall()
    except Exception as e:
        st.error(f"❌ Error cargando socias: {e}")
        return

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    dic_socias = {nombre: sid for sid, nombre in socias}

    socia_sel = st.selectbox("Seleccione la socia:", list(dic_socias.keys()))
    id_socia = dic_socias[socia_sel]


    # ==========================================
    # Cargar TIPOS DE MULTA desde tabla "Tipo de multa"
    # ==========================================
    try:
        cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
        tipos = cursor.fetchall()
    except Exception as e:
        st.error(f"❌ Error cargando tipos de multa: {e}")
        return

    if not tipos:
        st.warning("⚠ No hay tipos de multa configurados.")
        return

    dic_tipos = {nombre: tid for tid, nombre in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", list(dic_tipos.keys()))
    id_tipo = dic_tipos[tipo_sel]


    # ==========================================
    # Campos del formulario real
    # ==========================================
    monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado", ["A pagar", "Pagada"])

    # Opcionales:
    id_asistencia = st.number_input("ID Asistencia (opcional)", min_value=0, step=1)
    id_prestamo = st.number_input("ID Préstamo (opcional)", min_value=0, step=1)


    # ==========================================
    # GUARDAR REGISTRO EN LA TABLA MULTA
    # ==========================================
    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa 
                (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia, Id_Asistencia, Id_Préstamo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                monto,
                fecha,
                estado,
                id_tipo,
                id_socia,
                id_asistencia if id_asistencia != 0 else None,
                id_prestamo if id_prestamo != 0 else None
            ))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error al registrar la multa: {e}")

    cursor.close()
    con.close()



# ======================================================
# 4. REPORTES
# ======================================================
def pagina_reportes():
    st.header("📊 Actas y reportes del grupo")
    st.info("Aquí podrás generar reportes en el futuro.")

import streamlit as st
from modulos.conexion import obtener_conexion

# ========================================================
# PANEL PRINCIPAL
# ========================================================
def interfaz_directiva():
    st.title("👨‍💼 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ]

    seleccion = st.sidebar.radio("Selecciona una opción:", opciones)

    if seleccion == "Registrar reunión y asistencia":
        pagina_reunion()

    elif seleccion == "Registrar préstamos o pagos":
        pagina_prestamos()

    elif seleccion == "Aplicar multas":
        pagina_multas()

    elif seleccion == "Generar actas y reportes":
        pagina_reportes()


# ========================================================
# 1️⃣ REGISTRO DE REUNIÓN + ASISTENCIA
# ========================================================
def pagina_reunion():

    st.header("📅 Registro de reunión")
    
    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a MySQL.")
        return
    cursor = con.cursor()

    # --------------------------
    # Datos de la reunión
    # --------------------------
    fecha = st.date_input("Fecha de la reunión")
    tema = st.text_input("Tema principal")
    observacion = st.text_area("Observaciones generales")
    
    # Registrar reunión
    if st.button("💾 Registrar reunión"):
        try:
            cursor.execute("""
                INSERT INTO Reunion (Fecha_reunion, Tema_principal, Observaciones)
                VALUES (%s, %s, %s)
            """, (fecha, tema, observacion))
            con.commit()
            st.success("✔ Reunión registrada correctamente.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

    st.subheader("🗒 Registro de asistencia")

    # --------------------------
    # Registrar asistencia
    # --------------------------
    cursor.execute("SELECT Id_Usuario, Usuario FROM Usuario")
    usuarios = cursor.fetchall()

    if usuarios:
        dic_usuarios = {nombre: uid for uid, nombre in usuarios}
        usuario_sel = st.selectbox("Miembro", list(dic_usuarios.keys()))
        estado = st.selectbox("Estado", ["Asistió", "Faltó"])
        id_usuario = dic_usuarios[usuario_sel]

        if st.button("➕ Registrar asistencia"):
            try:
                cursor.execute("""
                    INSERT INTO Asistencia (Id_Usuario, Fecha_asistencia, Estado)
                    VALUES (%s, %s, %s)
                """, (id_usuario, fecha, estado))
                con.commit()
                st.success("✔ Asistencia registrada.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

    cursor.close()
    con.close()


# ========================================================
# 2️⃣ REGISTRO DE PRÉSTAMOS Y PAGOS
# ========================================================
def pagina_prestamos():

    st.header("💰 Registro de préstamos o pagos")

    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con MySQL.")
        return

    cursor = con.cursor()

    cursor.execute("SELECT Id_Usuario, Usuario FROM Usuario")
    usuarios = cursor.fetchall()

    if not usuarios:
        st.warning("⚠ No hay usuarios registrados.")
        return

    dic_usuarios = {nombre: uid for uid, nombre in usuarios}

    tipo = st.selectbox("Tipo de registro:", ["Préstamo", "Pago"])
    usuario_sel = st.selectbox("Seleccione el usuario:", list(dic_usuarios.keys()))
    id_usuario = dic_usuarios[usuario_sel]

    monto = st.number_input("Monto ($)", min_value=0.00)
    descripcion = st.text_area("Descripción del movimiento")

    if st.button("💾 Guardar movimiento"):
        try:
            if tipo == "Préstamo":
                cursor.execute("""
                    INSERT INTO Prestamo (Id_Usuario, Monto_solicitado, Observaciones)
                    VALUES (%s, %s, %s)
                """, (id_usuario, monto, descripcion))
            else:
                cursor.execute("""
                    INSERT INTO Pago (Id_Usuario, Monto_pagado, Observaciones)
                    VALUES (%s, %s, %s)
                """, (id_usuario, monto, descripcion))

            con.commit()
            st.success(f"✔ {tipo} registrado correctamente.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

    cursor.close()
    con.close()


# ========================================================
# 3️⃣ APLICACIÓN DE MULTAS — ADAPTADO A TU TABLA REAL
# ========================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con MySQL.")
        return

    cursor = con.cursor()

    # ------------------------------------
    # Cargar usuarios
    # ------------------------------------
    cursor.execute("SELECT Id_Usuario, Usuario FROM Usuario")
    usuarios = cursor.fetchall()

    if not usuarios:
        st.warning("⚠ No hay usuarios.")
        return

    dic_usuarios = {nombre: uid for uid, nombre in usuarios}

    usuario_sel = st.selectbox("Usuario sancionado:", list(dic_usuarios.keys()))
    id_usuario = dic_usuarios[usuario_sel]

    # ------------------------------------
    # Cargar tipos de multa
    # ------------------------------------
    cursor.execute("SELECT Id_Tipo_multa, Nombre_tipo FROM Tipo_de_multa")
    tipos = cursor.fetchall()

    if not tipos:
        st.warning("⚠ No hay tipos de multa configurados.")
        return

    dic_tipos = {nombre: tid for tid, nombre in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", list(dic_tipos.keys()))
    id_tipo = dic_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.00)
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado:", ["Pendiente", "Pagada"])

    # Opcionales
    id_asistencia = st.number_input("ID Asistencia (opcional)", min_value=0, step=1)
    id_prestamo = st.number_input("ID Préstamo (opcional)", min_value=0, step=1)

    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Usuario, Id_Asistencia, Id_Préstamo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                monto,
                fecha,
                estado,
                id_tipo,
                id_usuario,
                id_asistencia if id_asistencia != 0 else None,
                id_prestamo if id_prestamo != 0 else None
            ))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

    cursor.close()
    con.close()


# ========================================================
# 4️⃣ REPORTES
# ========================================================
def pagina_reportes():

    st.header("📊 Generar actas y reportes del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a MySQL.")
        return

    cursor = con.cursor()

    st.subheader("📌 Reporte rápido")

    try:
        cursor.execute("SELECT COUNT(*) FROM Reunion")
        total_reuniones = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Prestamo")
        total_prestamos = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Multa")
        total_multas = cursor.fetchone()[0]

        st.write(f"📅 Total de reuniones registradas: **{total_reuniones}**")
        st.write(f"💰 Total de préstamos registrados: **{total_prestamos}**")
        st.write(f"⚠ Total de multas aplicadas: **{total_multas}**")

    except Exception as e:
        st.error(f"❌ Error al generar reporte: {e}")

    cursor.close()
    con.close()

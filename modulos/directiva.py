def pagina_multas():
    st.subheader("⚠ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # 1️⃣ Cargar socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()

    lista_socias = {s[1]: s[0] for s in socias}

    seleccion_socia = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[seleccion_socia]

    # 2️⃣ Cargar tipos de multa
    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()

    lista_tipos = {t[1]: t[0] for t in tipos}

    seleccion_tipo = st.selectbox("📌 Tipo de multa:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[seleccion_tipo]

    # 3️⃣ Ingresar monto
    monto = st.number_input("💲 Monto de la multa:", min_value=0.00, step=0.25)

    # 4️⃣ Fecha de aplicación de la multa
    fecha_aplicacion = st.date_input("📅 Fecha de aplicación")

    # 5️⃣ Estado siempre será "A pagar"
    estado = "A pagar"

    # 6️⃣ Guardar en la base de datos
    if st.button("💾 Guardar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha_aplicacion, estado, id_tipo_multa, id_socia))

            con.commit()
            st.success("✅ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error al guardar multa: {e}")

    # 7️⃣ Mostrar multas registradas
    st.divider()
    st.subheader("📋 Multas registradas")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`, M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        ORDER BY M.Id_Multa DESC
    """)
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos, columns=["ID", "Socia", "Tipo", "Monto", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("Aún no hay multas registradas.")

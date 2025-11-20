import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

# MÓDULOS INTERNOS
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.reporte_caja import reporte_caja      # Reporte de Caja por Reunión
from modulos.caja import obtener_saldo_actual      # Saldo actual según caja_reunion


# ============================================================
# PANEL PRINCIPAL DIRECTIVA
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    # Validación de rol
    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    # Título
    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # ------------------------------------------------------
    # MOSTRAR SALDO ACTUAL DE CAJA (Opción A)
    # ------------------------------------------------------
    try:
        saldo = obtener_saldo_actual()
        st.info(f"💰 Saldo actual de caja: **${saldo}**")
    except:
        st.warning("⚠ Error al obtener el saldo de Caja (Opción A).")

    # Botón cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # Menú lateral
    menu = st.sidebar.radio(
        "Selección rápida:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro",
            "Reporte de caja"
        ]
    )

    # ENRUTAMIENTO DE PÁGINAS
    if menu == "Registro de asistencia":
        pagina_asistencia()

    elif menu == "Aplicar multas":
        pagina_multas()

    elif menu == "Registrar nuevas socias":
        pagina_registro_socias()

    elif menu == "Autorizar préstamo":
        autorizar_prestamo()

    elif menu == "Registrar pago de préstamo":
        pago_prestamo()

    elif menu == "Registrar ahorro":
        ahorro()

    elif menu == "Reporte de caja":
        reporte_caja()



# ============================================================
# REGISTRO DE ASISTENCIA + INGRESOS EXTRAORDINARIOS
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cursor = con.cursor()

    # Fecha de reunión
    fecha_raw = st.date_input("📅 Fecha de la reunión", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Buscar reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion=%s", (fecha,))
    row = cursor.fetchone()

    # Crear reunión si no existe
    if row:
        id_reunion = row[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion(Fecha_reunion, Observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES(%s,'','','',1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.success(f"Reunión creada correctamente (ID {id_reunion}).")

    # Lista de socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")
    asistencia_registro = {}

    for id_socia, nombre in socias:
        asistencia = st.selectbox(
            f"{id_socia} - {nombre}",
            ["SI", "NO"],
            key=f"asis_{id_socia}"
        )
        asistencia_registro[id_socia] = asistencia

    # Guardar asistencia
    if st.button("💾 Guardar asistencia"):
        for id_socia, asis in asistencia_registro.items():
            estado = "Presente" if asis == "SI" else "Ausente"

            cursor.execute("""
                SELECT Id_Asistencia
                FROM Asistencia
                WHERE Id_Reunion=%s AND Id_Socia=%s
            """, (id_reunion, id_socia))

            existe = cursor.fetchone()

            if existe:
                cursor.execute("""
                    UPDATE Asistencia 
                    SET Estado_asistencia=%s, Fecha=%s
                    WHERE Id_Reunion=%s AND Id_Socia=%s
                """, (estado, fecha, id_reunion, id_socia))
            else:
                cursor.execute("""
                    INSERT INTO Asistencia(Id_Reunion,Id_Socia,Estado_asistencia,Fecha)
                    VALUES(%s,%s,%s,%s)
                """, (id_reunion, id_socia, estado, fecha))

        con.commit()
        st.success("Asistencia actualizada.")

    # Mostrar registro
    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia=A.Id_Socia
        WHERE A.Id_Reunion=%s
    """, (id_reunion,))
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["Socia", "Asistencia"])
        st.dataframe(df)

        total_presentes = df[df.Asistencia == "Presente"].shape[0]
        st.success(f"Total presentes: {total_presentes}")

    st.markdown("---")

    # ============================================================
    # INGRESOS EXTRAORDINARIOS
    # ============================================================
    st.header("💰 Ingresos extraordinarios")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista_socias = cursor.fetchall()
    opc_socias = {nombre: id_s for id_s, nombre in lista_socias}

    socia_sel = st.selectbox("Socia que aporta:", opc_socias.keys())
    id_socia = opc_socias[socia_sel]

    tipo = st.selectbox("Tipo", ["Rifa", "Donación", "Actividad", "Otro"])
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)

    if st.button("➕ Registrar ingreso extraordinario"):

        cursor.execute("""
            INSERT INTO IngresosExtra(Id_Reunion,Id_Socia,Tipo,Descripcion,Monto,Fecha)
            VALUES(%s,%s,%s,%s,%s,%s)
        """, (id_reunion, id_socia, tipo, descripcion, monto, fecha))

        con.commit()
        st.success("Ingreso extraordinario registrado.")
        st.rerun()



# ============================================================
# MULTAS
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_s for id_s, nombre in socias}

    socia_sel = st.selectbox("Socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    lista_tipos = {nombre: id_t for id_t, nombre in tipos}

    tipo_sel = st.selectbox("Tipo:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)
    fecha_raw = st.date_input("Fecha", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        cursor.execute("""
            INSERT INTO Multa(Monto,Fecha_aplicacion,Estado,Id_Tipo_multa,Id_Socia)
            VALUES(%s,%s,%s,%s,%s)
        """, (monto, fecha, estado, id_tipo_multa, id_socia))

        con.commit()
        st.success("Multa registrada.")
        st.rerun()



# ============================================================
# REGISTRO DE SOCIAS
# ============================================================
def pagina_registro_socias():

    st.header("👩‍🦰 Registro de socias")

    con = obtener_conexion()
    cursor = con.cursor()

    nombre = st.text_input("Nombre completo")

    if st.button("Registrar socia"):

        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre.")
            return

        cursor.execute("INSERT INTO Socia(Nombre,Sexo) VALUES(%s,'F')", (nombre,))
        con.commit()

        st.success("Socia registrada.")
        st.rerun()

    cursor.execute("SELECT Id_Socia,Nombre FROM Socia ORDER BY Id_Socia ASC")
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos, columns=["ID","Nombre"])
        st.dataframe(df)

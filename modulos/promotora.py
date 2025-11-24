import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# =============================================================================
# OBTENER ID EMPLEADO (PROMOTORA)
# =============================================================================
def obtener_id_promotora():
    """Retorna el Id_Empleado de la promotora logueada."""
    usuario = st.session_state.get("usuario", "")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Empleado 
        FROM Empleado 
        WHERE Usuario = %s AND Rol = 'Promotora'
    """, (usuario,))

    row = cursor.fetchone()

    cursor.close()
    con.close()

    return row["Id_Empleado"] if row else None



# =============================================================================
# PÁGINA PRINCIPAL DE PROMOTORA — CON MENÚ CENTRADO
# =============================================================================
def interfaz_promotora():

    # ------------------ TÍTULO CENTRADO ------------------
    st.markdown("""
        <h1 style="text-align:center;">
            👩‍🦰 Panel de Promotora — Solidaridad CVX
        </h1>
        <br>
    """, unsafe_allow_html=True)

    # ------------------ CERRAR SESIÓN ------------------
    col1, col2 = st.columns([8, 2])
    with col2:
        if st.button("Cerrar sesión"):
            st.session_state["sesion_iniciada"] = False
            st.session_state["rol"] = None
            st.rerun()

    # ------------------ VALIDAR PROMOTORA ------------------
    id_promotora = obtener_id_promotora()
    if not id_promotora:
        st.error("⚠ No se pudo validar la promotora. Verifica el usuario.")
        return

    # ------------------ MENÚ HORIZONTAL ------------------
    tabs = st.tabs([
        "➕ Crear grupo",
        "📘 Gestionar grupos",
        "📋 Ver grupos"
    ])

    # CREAR GRUPO
    with tabs[0]:
        st.subheader("➕ Crear nuevo grupo")
        crear_grupo(id_promotora)

    # EDITAR + ELIMINAR GRUPO
    with tabs[1]:
        st.subheader("📘 Gestionar grupos (editar / eliminar)")
        gestionar_grupos(id_promotora)

    # VER GRUPOS
    with tabs[2]:
        st.subheader("📋 Lista de grupos")
        ver_grupos(id_promotora)



# =============================================================================
# CREAR GRUPO — NUEVO PROCESO COMPLETO
# =============================================================================
def crear_grupo(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Obtener DUI real de la promotora logueada
    cursor.execute("SELECT DUI FROM Empleado WHERE Id_Empleado = %s", (id_promotora,))
    promotora = cursor.fetchone()
    dui_promotora_real = promotora["DUI"]

    # ------------------ PASO 1: DUI PARA VALIDAR IDENTIDAD ------------------
    st.write("### 🔒 Paso 1 — Validar identidad de la promotora")

    dui_ingresado = st.text_input("Ingrese su DUI (9 dígitos)").strip()

    if dui_ingresado:
        if not dui_ingresado.isdigit() or len(dui_ingresado) != 9:
            st.error("❌ El DUI debe ser exactamente 9 dígitos.")
            return
        if dui_ingresado != dui_promotora_real:
            st.error("❌ El DUI no coincide con la promotora logueada.")
            return

    # ------------------ PASO 2: CREAR USUARIO INTERNO ------------------
    st.write("---")
    st.write("### 👤 Paso 2 — Crear usuario interno del grupo")

    usuario_grupo = st.text_input("Usuario del grupo").strip()
    password_grupo = st.text_input("Contraseña del grupo", type="password")

    # Validar usuario no repetido
    usuario_disponible = False
    if usuario_grupo != "":
        cursor.execute("SELECT * FROM Empleado WHERE Usuario = %s", (usuario_grupo,))
        existe = cursor.fetchone()
        if existe:
            st.error("❌ Usuario ya existente. Ingrese uno diferente.")
        else:
            usuario_disponible = True

    # ------------------ PASO 3: DATOS BÁSICOS DEL GRUPO ------------------
    st.write("---")
    st.write("### 📝 Paso 3 — Información del grupo")

    nombre = st.text_input("Nombre del grupo")
    tasa = st.number_input("Tasa de interés (%)", min_value=0.0, step=0.1)
    periodicidad = st.number_input("Periodicidad de reuniones (días)", min_value=1, step=1)
    distrito = st.number_input("ID del distrito", min_value=1, step=1)
    fecha_inicio = st.date_input("Fecha de inicio", value=date.today())

    # Validar que todo esté bien
    datos_ok = (
        dui_ingresado == dui_promotora_real
        and usuario_grupo.strip() != ""
        and password_grupo.strip() != ""
        and usuario_disponible
        and nombre.strip() != ""
    )

    # ------------------ CREAR GRUPO ------------------
    if st.button("Crear grupo", disabled=not datos_ok, type="primary"):

        # Crear usuario Directiva del grupo
        cursor.execute("""
            INSERT INTO Empleado (Nombres, Apellidos, DUI, Usuario, Contrasena, Rol)
            VALUES (%s, %s, %s, %s, %s, 'Directiva')
        """, (
            "Directiva " + nombre,
            "",
            dui_promotora_real,
            usuario_grupo,
            password_grupo
        ))

        id_directiva = cursor.lastrowid

        # Crear grupo nuevo
        cursor.execute("""
            INSERT INTO Grupo(
                Nombre_grupo, Tasa_de_interes, Periodicidad_reuniones,
                Fecha_inicio, Id_Promotora, Id_Distrito, Id_Directiva
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (
            nombre, tasa, periodicidad, fecha_inicio,
            id_promotora, distrito, id_directiva
        ))

        con.commit()
        cursor.close()
        con.close()

        st.success("✅ Grupo creado correctamente con su usuario interno.")
        st.rerun()



# =============================================================================
# VER GRUPOS
# =============================================================================
def ver_grupos(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT * 
        FROM Grupo
        WHERE Id_Promotora = %s
        ORDER BY Id_Grupo DESC
    """, (id_promotora,))

    grupos = cursor.fetchall()

    cursor.close()
    con.close()

    if not grupos:
        st.info("No tienes grupos registrados.")
        return

    df = pd.DataFrame(grupos)
    st.dataframe(df, hide_index=True)



# =============================================================================
# GESTIONAR GRUPOS (EDITAR + ELIMINAR)
# =============================================================================
def gestionar_grupos(id_promotora):

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Grupo, Nombre_grupo
        FROM Grupo
        WHERE Id_Promotora=%s
    """, (id_promotora,))

    grupos = cursor.fetchall()

    if not grupos:
        st.info("No hay grupos disponibles.")
        return

    opciones = {g["Nombre_grupo"]: g["Id_Grupo"] for g in grupos}
    sel = st.selectbox("Seleccione un grupo:", opciones.keys())
    id_g = opciones[sel]

    cursor.execute("SELECT * FROM Grupo WHERE Id_Grupo=%s", (id_g,))
    g = cursor.fetchone()

    st.write("### ✏️ Editar grupo")

    nombre = st.text_input("Nombre", g["Nombre_grupo"])
    tasa = st.number_input("Tasa (%)", value=float(g["Tasa_de_interes"]))
    periodicidad = st.number_input("Periodicidad", value=g["Periodicidad_reuniones"])
    distrito = st.number_input("ID Distrito", value=g["Id_Distrito"])
    fecha_inicio = st.date_input("Fecha inicio", value=g["Fecha_inicio"])

    if st.button("Guardar cambios", type="primary"):
        cursor.execute("""
            UPDATE Grupo SET
                Nombre_grupo=%s, Tasa_de_interes=%s,
                Periodicidad_reuniones=%s, Id_Distrito=%s,
                Fecha_inicio=%s
            WHERE Id_Grupo=%s
        """, (nombre, tasa, periodicidad, distrito, fecha_inicio, id_g))

        con.commit()
        st.success("Cambios guardados.")
        st.rerun()

    st.write("---")
    st.write("### 🗑️ Eliminar grupo")

    if st.button("Eliminar grupo definitivamente"):
        cursor.execute("DELETE FROM Grupo WHERE Id_Grupo=%s", (id_g,))
        con.commit()

        st.error("Grupo eliminado permanentemente.")
        st.rerun()

    cursor.close()
    con.close()

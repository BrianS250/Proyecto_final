import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# ============================================================
#              PANEL PRINCIPAL DEL ADMINISTRADOR
# ============================================================
def interfaz_admin():
    # Seguridad: solo usuarios con rol "Administrador"
    rol = st.session_state.get("rol", "")
    if rol != "Administrador":
        st.error("⛔ No tiene permisos para acceder al panel de administrador.")
        return

    st.title("🛡️ Panel del Administrador")
    st.caption("Gestione roles, distritos, grupos y empleados del sistema.")

    # --------------------------------------------------------
    # Métricas generales (tarjetas superiores)
    # --------------------------------------------------------

        # --------------------------------------------------------
    # Métricas generales (tarjetas superiores)
    # --------------------------------------------------------
    col1, col2, col3, col4 = st.columns(4)
    try:
        con = obtener_conexion()
        cur = con.cursor()

        # Distritos
        cur.execute("SELECT COUNT(*) FROM Distrito")
        total_distritos = cur.fetchone()[0]

        # Grupos
        cur.execute("SELECT COUNT(*) FROM Grupo")
        total_grupos = cur.fetchone()[0]

        # Promotoras = empleados cuyo Rol sea 'Promotora'
        cur.execute("SELECT COUNT(*) FROM Empleado WHERE Rol = 'Promotora'")
        total_promotoras = cur.fetchone()[0]

        # Empleados totales
        cur.execute("SELECT COUNT(*) FROM Empleado")
        total_empleados = cur.fetchone()[0]

        col1.metric("🏙 Distritos", total_distritos)
        col2.metric("👥 Grupos", total_grupos)
        col3.metric("👩‍💼 Promotoras", total_promotoras)
        col4.metric("🧑‍💻 Empleados", total_empleados)

    except Exception as e:
        st.warning(f"No se pudieron cargar las métricas: {e}")
    finally:
        try:
            cur.close()
            con.close()
        except:
            pass

  

    st.markdown("---")

    # --------------------------------------------------------
    # Menú lateral de administración
    # --------------------------------------------------------
    seccion = st.sidebar.radio(
        "📂 Módulos de administración",
        [
            "Gestión de roles",
            "Gestión de distritos",
            "Gestión de grupos",
            "Gestión de promotoras",
            "Gestión de empleados",
            "Resumen general", 
        ]
    )

    if seccion == "Gestión de roles":
        gestion_roles()
    elif seccion == "Gestión de distritos":
        gestion_distritos()
    elif seccion == "Gestión de grupos":
        gestion_grupos()
    elif seccion == "Gestión de promotoras":
        gestion_promotoras()
    elif seccion == "Gestión de empleados":
        gestion_empleados()

    elif seccion == "Resumen general":
        resumen_general()  


# ============================================================
#                      GESTIÓN DE ROLES
# ============================================================
def gestion_roles():
    st.header("🎭 Gestión de roles")

    con = obtener_conexion()
    cursor = con.cursor()

    col1, col2 = st.columns([2, 1])

    with col1:
        nuevo_rol = st.text_input(
            "Nombre del nuevo rol (ej: Director, Promotora, Administrador)"
        )

    with col2:
        if st.button("➕ Crear rol"):
            if nuevo_rol.strip() == "":
                st.warning("Debe escribir un nombre de rol.")
            else:
                try:
                    cursor.execute(
                        "INSERT INTO Roles(Tipo_de_rol) VALUES(%s)",
                        (nuevo_rol,),
                    )
                    con.commit()
                    st.success("Rol creado correctamente.")
                except Exception as e:
                    st.error(f"Error al crear rol: {e}")

    st.markdown("### 📋 Roles existentes")
    try:
        cursor.execute("SELECT Id_Roles, Tipo_de_rol FROM Roles ORDER BY Id_Roles ASC")
        roles = cursor.fetchall()
        if roles:
            df = pd.DataFrame(roles, columns=["ID", "Tipo de rol"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay roles registrados.")
    except Exception as e:
        st.error(f"Error al consultar roles: {e}")

    cursor.close()
    con.close()


# ============================================================
#                   GESTIÓN DE DISTRITOS
# ============================================================
def gestion_distritos():
    st.header("🏙 Gestión de distritos")

    con = obtener_conexion()
    cursor = con.cursor()

    st.subheader("➕ Crear nuevo distrito")

    nombre = st.text_input("Nombre del distrito")
    col1, col2 = st.columns(2)
    with col1:
        representantes = st.number_input("Número de representantes", min_value=0, step=1, value=0)
    with col2:
        # Ver punto 2 sobre este campo 👇
        cant_grupos = st.number_input("Cantidad de grupos (inicial)", min_value=0, step=1, value=0)

    estado = st.selectbox("Estado del distrito", ["Activo", "Inactivo", "En formación"])

    if st.button("Crear distrito"):
        if nombre.strip() == "":
            st.warning("El nombre del distrito es obligatorio.")
        else:
            try:
                cursor.execute(
                    """
                    INSERT INTO Distrito(
                        Nombre_distrito,
                        Representantes,
                        Cantidad_grupos,
                        Estado_distrito
                    )
                    VALUES(%s, %s, %s, %s)
                    """,
                    (
                        nombre,
                        int(representantes),
                        int(cant_grupos),
                        estado,
                    ),
                )
                con.commit()
                st.success("Distrito creado correctamente.")
            except Exception as e:
                st.error(f"Error al crear distrito: {e}")

    st.markdown("### 📋 Distritos registrados")

    try:
        cursor.execute(
            """
            SELECT Id_Distrito,
                   Nombre_distrito,
                   Representantes,
                   Cantidad_grupos,
                   Estado_distrito
            FROM Distrito
            ORDER BY Id_Distrito ASC
            """
        )
        distritos = cursor.fetchall()
        if distritos:
            df = pd.DataFrame(
                distritos,
                columns=["ID", "Nombre", "Representantes", "Cant. grupos", "Estado"],
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay distritos registrados.")
    except Exception as e:
        st.error(f"Error al consultar distritos: {e}")

    cursor.close()
    con.close()


# ============================================================
#                     GESTIÓN DE GRUPOS
# ============================================================
def gestion_grupos():
    st.header("👥 Gestión de grupos")

    con = obtener_conexion()
    cursor = con.cursor()

    # --------------------------------------------------------
    # Cargar distritos
    # --------------------------------------------------------
    try:
        cursor.execute(
            "SELECT Id_Distrito, Nombre_distrito FROM Distrito ORDER BY Id_Distrito ASC"
        )
        distritos = cursor.fetchall()
        dict_distritos = {f"{d[0]} - {d[1]}": d[0] for d in distritos} if distritos else {}
    except Exception as e:
        st.error(f"Error al cargar distritos: {e}")
        dict_distritos = {}

    # --------------------------------------------------------
    # Cargar promotoras (empleados con rol 'Promotora')
    # Usa Empleado.Id_Rol (singular) contra Roles.Id_Roles
    # --------------------------------------------------------
    try:
        cursor.execute(
            """
            SELECT e.Id_Empleado, e.Nombres, e.Apellidos
            FROM Empleado e
            LEFT JOIN Roles r ON e.Id_Rol = r.Id_Roles
            WHERE r.Tipo_de_rol = 'Promotora'
               OR e.Rol = 'Promotora'
            ORDER BY e.Id_Empleado ASC
            """
        )
        promotoras = cursor.fetchall()
        dict_prom = {
            f"{p[0]} - {p[1]} {p[2]}": p[0] for p in promotoras
        } if promotoras else {}
    except Exception as e:
        st.error(f"Error al cargar promotoras: {e}")
        dict_prom = {}

    # --------------------------------------------------------
    # Cargar directivas (empleados con rol 'Director')
    # --------------------------------------------------------
    try:
        cursor.execute(
            """
            SELECT e.Id_Empleado, e.Nombres, e.Apellidos
            FROM Empleado e
            LEFT JOIN Roles r ON e.Id_Rol = r.Id_Roles
            WHERE r.Tipo_de_rol = 'Director'
               OR e.Rol = 'Director'
            ORDER BY e.Id_Empleado ASC
            """
        )
        directores = cursor.fetchall()
        dict_dir = {
            f"{d[0]} - {d[1]} {d[2]}": d[0] for d in directores
        } if directores else {}
    except Exception as e:
        st.error(f"Error al cargar directores: {e}")
        dict_dir = {}

    # --------------------------------------------------------
    # Elegir un tipo de multa por defecto (no se muestra en UI)
    # --------------------------------------------------------
    default_tipo_multa_id = None
    try:
        cursor.execute(
            "SELECT Id_Tipo_multa FROM `Tipo de multa` ORDER BY Id_Tipo_multa ASC LIMIT 1"
        )
        row = cursor.fetchone()
        if row:
            default_tipo_multa_id = row[0]
    except Exception as e:
        st.error(f"Error al cargar tipo de multa por defecto: {e}")

    st.subheader("➕ Crear nuevo grupo")

    # ---------------------- CAMPOS VISIBLES ------------------
    nombre_grupo = st.text_input("Nombre del grupo")

    fecha_inicio = st.date_input("Fecha de inicio del grupo", value=date.today())

    distrito_sel = st.selectbox(
        "Distrito del grupo",
        list(dict_distritos.keys()) if dict_distritos else ["(No hay distritos registrados)"],
    )

    promotora_sel = st.selectbox(
        "Promotora asignada",
        list(dict_prom.keys()) if dict_prom else ["(No hay promotoras registradas)"],
    )

    opciones_director = ["(Sin director por ahora)"]
    if dict_dir:
        opciones_director += list(dict_dir.keys())

    director_sel = st.selectbox(
        "Director del grupo (opcional)",
        opciones_director,
    )

    # ---------------------- GUARDAR GRUPO --------------------
    if st.button("Crear grupo"):
        if nombre_grupo.strip() == "":
            st.warning("El nombre del grupo es obligatorio.")
        elif not dict_distritos or distrito_sel not in dict_distritos:
            st.warning("Debe seleccionar un distrito válido.")
        elif not dict_prom or promotora_sel not in dict_prom:
            st.warning("Debe seleccionar una promotora válida.")
        elif default_tipo_multa_id is None:
            st.warning("Debe existir al menos un tipo de multa en la tabla 'Tipo de multa'.")
        else:
            try:
                id_distrito = dict_distritos[distrito_sel]
                id_prom = dict_prom[promotora_sel]

                if director_sel != "(Sin director por ahora)" and director_sel in dict_dir:
                    id_directiva = dict_dir[director_sel]
                else:
                    id_directiva = None

                # Valores por defecto para campos no visibles
                tasa_interes = 0.0
                periodicidad = fecha_inicio
                reglas_texto = "Se aplican las reglas generales del programa de ahorro y crédito."

                cursor.execute(
                    """
                    INSERT INTO Grupo(
                        Nombre_grupo,
                        Tasa_de_interes,
                        Periodicidad_reuniones,
                        Id_Tipo_multa,
                        Reglas_de_prestamo,
                        Fecha_inicio,
                        Id_Promotora,
                        Id_Distrito,
                        Id_Directiva        -- 👈 AQUÍ va el nuevo nombre
                    )
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        nombre_grupo,
                        tasa_interes,
                        periodicidad,
                        default_tipo_multa_id,
                        reglas_texto,
                        fecha_inicio,
                        id_prom,
                        id_distrito,
                        id_directiva,
                    ),
                )
                con.commit()
                st.success("Grupo creado correctamente.")
            except Exception as e:
                st.error(f"Error al crear grupo: {e}")

    # --------------------------------------------------------
    # Tabla de grupos registrados (resumen)
    # --------------------------------------------------------
    st.markdown("### 📋 Grupos registrados")

    try:
        cursor.execute(
            """
            SELECT g.Id_Grupo,
                   g.Nombre_grupo,
                   d.Nombre_distrito,
                   CONCAT(p.Nombres, ' ', p.Apellidos) AS Promotora,
                   CONCAT(
                       COALESCE(dir.Nombres, ''),
                       CASE WHEN dir.Nombres IS NULL THEN '' ELSE ' ' END,
                       COALESCE(dir.Apellidos, '')
                   ) AS Director,
                   g.Fecha_inicio
            FROM Grupo g
            JOIN Distrito d ON g.Id_Distrito   = d.Id_Distrito
            JOIN Empleado p ON g.Id_Promotora  = p.Id_Empleado
            LEFT JOIN Empleado dir ON g.Id_Directiva = dir.Id_Empleado   -- 👈 AQUÍ también
            ORDER BY g.Id_Grupo ASC
            """
        )
        grupos = cursor.fetchall()
        if grupos:
            df = pd.DataFrame(
                grupos,
                columns=["ID", "Nombre de grupo", "Distrito", "Promotora", "Director", "Fecha inicio"],
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay grupos registrados.")
    except Exception as e:
        st.error(f"Error al consultar grupos: {e}")

    cursor.close()
    con.close()



# ============================================================
#            GESTIÓN DE PROMOTORAS (vista filtrada)
# ============================================================
def gestion_promotoras():
    st.header("👩‍💼 Gestión de promotoras (empleados con rol Promotora)")

    con = obtener_conexion()
    cursor = con.cursor()

    # Obtener Id_Roles de 'Promotora'
    try:
        cursor.execute(
            "SELECT Id_Roles FROM Roles WHERE Tipo_de_rol = 'Promotora' LIMIT 1"
        )
        row = cursor.fetchone()
        if not row:
            st.error("No existe el rol 'Promotora' en la tabla Roles.")
            cursor.close()
            con.close()
            return
        id_rol_promotora = row[0]
    except Exception as e:
        st.error(f"Error al obtener rol Promotora: {e}")
        cursor.close()
        con.close()
        return

    # Cargar distritos (usar Nombre_distrito, SIN espacios)
    try:
        cursor.execute(
            "SELECT Id_Distrito, Nombre_distrito FROM Distrito ORDER BY Id_Distrito ASC"
        )
        distritos = cursor.fetchall()
        dict_distritos = {f"{d[0]} - {d[1]}": d[0] for d in distritos} if distritos else {}
    except Exception as e:
        st.error(f"Error al cargar distritos: {e}")
        dict_distritos = {}

    st.subheader("➕ Registrar nueva promotora")

    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario")
        contra = st.text_input("Contraseña", type="password")
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
    with col2:
        telefono = st.text_input("Teléfono")
        dui = st.text_input("DUI")
        distrito_sel = st.selectbox(
            "Distrito base",
            list(dict_distritos.keys()) if dict_distritos else ["(Sin distritos)"],
        )
        estado = st.selectbox("Estado", ["Activo", "Inactivo"])

    if st.button("Registrar promotora"):
        if usuario.strip() == "" or contra.strip() == "":
            st.warning("Usuario y contraseña son obligatorios.")
        elif not dict_distritos or distrito_sel not in dict_distritos:
            st.warning("Debe seleccionar un distrito válido.")
        else:
            try:
                id_distrito = dict_distritos[distrito_sel]

                cursor.execute(
                    """
                    INSERT INTO Empleado(
                        Usuario,
                        Contra,
                        Rol,
                        Nombres,
                        Apellidos,
                        DUI,
                        Telefono,
                        Distrito,
                        Estado,
                        Id_Rol
                    )
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        usuario,
                        contra,
                        "Promotora",        # texto legacy
                        nombres,
                        apellidos,
                        dui,
                        telefono,
                        id_distrito,
                        estado,
                        id_rol_promotora,  # FK a Roles
                    ),
                )
                con.commit()
                st.success("Promotora registrada correctamente.")
            except Exception as e:
                st.error(f"Error al registrar promotora: {e}")

    st.markdown("### 📋 Promotoras registradas")

    try:
        cursor.execute(
            """
            SELECT e.Id_Empleado,
                   e.Usuario,
                   e.Nombres,
                   e.Apellidos,
                   d.Nombre_distrito,
                   e.Estado
           FROM Empleado e
           JOIN Roles r ON e.Id_Rol = r.Id_Roles      -- 👈 aquí
           LEFT JOIN Distrito d ON e.Distrito = d.Id_Distrito
           WHERE r.Tipo_de_rol = 'Promotora'

            ORDER BY e.Id_Empleado ASC
            """
        )
        promotoras = cursor.fetchall()
        if promotoras:
            df = pd.DataFrame(
                promotoras,
                columns=["ID", "Usuario", "Nombres", "Apellidos", "Distrito", "Estado"],
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay promotoras registradas.")
    except Exception as e:
        st.error(f"Error al consultar promotoras: {e}")

    cursor.close()
    con.close()



# ============================================================
#                   GESTIÓN DE EMPLEADOS
# ============================================================
def gestion_empleados():
    st.header("🧑‍💻 Gestión de empleados (usuarios del sistema)")

    con = obtener_conexion()
    cursor = con.cursor()

    # Cargar roles desde la tabla Roles
    try:
        cursor.execute("SELECT Id_Roles, Tipo_de_rol FROM Roles ORDER BY Id_Roles ASC")
        roles = cursor.fetchall()
        # Guardamos ID y texto del rol
        #   clave visible:  "3 - Director"
        #   valor interno:  (3, "Director")
        dict_roles = {f"{r[0]} - {r[1]}": (r[0], r[1]) for r in roles} if roles else {}
    except Exception as e:
        st.error(f"Error al cargar roles: {e}")
        dict_roles = {}
        roles = []

    # Cargar distritos para asignar al empleado
    try:
        cursor.execute(
            "SELECT Id_Distrito, Nombre_distrito FROM Distrito ORDER BY Id_Distrito ASC"
        )
        distritos = cursor.fetchall()
        dict_distritos = {f"{d[0]} - {d[1]}": d[0] for d in distritos} if distritos else {}
    except Exception as e:
        st.error(f"Error al cargar distritos: {e}")
        dict_distritos = {}

    st.subheader("➕ Crear nuevo empleado")

    col1, col2 = st.columns(2)
    with col1:
        usuario = st.text_input("Usuario (para inicio de sesión)")
        contra = st.text_input("Contraseña", type="password")
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
    with col2:
        dui = st.text_input("DUI")
        telefono = st.text_input("Teléfono")
        distrito_sel = st.selectbox(
            "Distrito asignado",
            list(dict_distritos.keys()) if dict_distritos else ["(Sin distritos)"],
        )
        estado = st.selectbox("Estado", ["Activo", "Inactivo"])

    rol_sel = st.selectbox(
        "Rol del empleado",
        list(dict_roles.keys()) if dict_roles else ["(No hay roles registrados)"],
    )

    if st.button("Crear empleado"):
        if usuario.strip() == "" or contra.strip() == "":
            st.warning("Usuario y contraseña son obligatorios.")
        elif not dict_roles or rol_sel not in dict_roles:
            st.warning("Debe seleccionar un rol válido.")
        elif not dict_distritos or distrito_sel not in dict_distritos:
            st.warning("Debe seleccionar un distrito válido.")
        else:
            try:
                id_rol, rol_texto = dict_roles[rol_sel]   # (Id_Roles, 'Director', etc.)
                id_distrito = dict_distritos[distrito_sel]

                # IMPORTANTE: ahora también insertamos Id_Rol
                cursor.execute(
                    """
                    INSERT INTO Empleado(
                        Usuario,
                        Contra,
                        Id_Rol,
                        Rol,
                        Nombres,
                        Apellidos,
                        DUI,
                        Telefono,
                        Distrito,
                        Estado
                    )
                    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        usuario,
                        contra,
                        id_rol,      # FK a Roles
                        rol_texto,   # texto ('Director','Promotora', etc.)
                        nombres,
                        apellidos,
                        dui,
                        telefono,
                        id_distrito,
                        estado,
                    ),
                )
                con.commit()
                st.success("Empleado creado correctamente.")
            except Exception as e:
                st.error(f"Error al crear empleado: {e}")

    st.markdown("### 📋 Empleados registrados")

    # -------------------------------
    # Filtro por rol
    # -------------------------------
    st.subheader("🔍 Filtros")

    opciones_filtro = ["(Todos los roles)"]
    if roles:
        opciones_filtro += [r[1] for r in roles]  # Tipo_de_rol

    rol_filtro = st.selectbox(
        "Filtrar por rol",
        opciones_filtro
    )

    try:
        sql = """
            SELECT e.Id_Empleado,
                   e.Usuario,
                   e.Rol,
                   e.Nombres,
                   e.Apellidos,
                   d.Nombre_distrito,
                   e.Estado
            FROM Empleado e
            LEFT JOIN Distrito d ON e.Distrito = d.Id_Distrito
        """
        params = []

        if rol_filtro != "(Todos los roles)":
            sql += " WHERE e.Rol = %s"
            params.append(rol_filtro)

        sql += " ORDER BY e.Id_Empleado ASC"

        cursor.execute(sql, params)
        empleados = cursor.fetchall()

        if empleados:
            df = pd.DataFrame(
                empleados,
                columns=["ID", "Usuario", "Rol", "Nombres", "Apellidos", "Distrito", "Estado"],
            )
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hay empleados registrados con ese filtro.")
    except Exception as e:
        st.error(f"Error al consultar empleados: {e}")

    cursor.close()
    con.close()


# ============================================================
#                   RESUMEN GENERAL (VISTA GLOBAL)
# ============================================================
def resumen_general():
    st.header("📊 Resumen general de grupos, promotoras y distritos")

    con = obtener_conexion()
    cursor = con.cursor()

    # ------------------------------------------------------------------
    # 1) Tabla base de GRUPOS (incluye promotora y DIRECTIVA)
    # ------------------------------------------------------------------
    try:
        cursor.execute(
            """
            SELECT g.Id_Grupo,
                   g.Nombre_grupo,
                   d.Nombre_distrito AS Distrito,
                   CONCAT(p.Nombres, ' ', p.Apellidos) AS Promotora,
                   CONCAT(
                       COALESCE(dir.Nombres, ''),
                       CASE WHEN dir.Nombres IS NULL THEN '' ELSE ' ' END,
                       COALESCE(dir.Apellidos, '')
                   ) AS Directiva,
                   g.Fecha_inicio
            FROM Grupo g
            JOIN Distrito d        ON g.Id_Distrito   = d.Id_Distrito
            JOIN Empleado p        ON g.Id_Promotora  = p.Id_Empleado
            LEFT JOIN Empleado dir ON g.Id_Directiva  = dir.Id_Empleado
            ORDER BY g.Id_Grupo ASC
            """
        )
        grupos = cursor.fetchall()
        df_grupos = pd.DataFrame(
            grupos,
            columns=[
                "ID grupo",
                "Nombre de grupo",
                "Distrito",
                "Promotora",
                "Directiva",
                "Fecha inicio",
            ],
        ) if grupos else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar grupos: {e}")
        df_grupos = pd.DataFrame()

    # ------------------------------------------------------------------
    # 2) Resumen por PROMOTORA
    # ------------------------------------------------------------------
    try:
        cursor.execute(
            """
            SELECT e.Id_Empleado,
                   CONCAT(e.Nombres, ' ', e.Apellidos) AS Promotora,
                   IFNULL(
                     GROUP_CONCAT(DISTINCT d.Nombre_distrito
                                  ORDER BY d.Nombre_distrito SEPARATOR ', '),
                     ''
                   ) AS Distritos,
                   COUNT(g.Id_Grupo) AS Total_grupos
            FROM Empleado e
            LEFT JOIN Grupo g    ON g.Id_Promotora = e.Id_Empleado
            LEFT JOIN Distrito d ON g.Id_Distrito  = d.Id_Distrito
            WHERE e.Rol = 'Promotora' OR e.Id_Rol IN (
                SELECT Id_Roles FROM Roles WHERE Tipo_de_rol = 'Promotora'
            )
            GROUP BY e.Id_Empleado, Promotora
            ORDER BY Promotora ASC
            """
        )
        promos = cursor.fetchall()
        df_promotoras = pd.DataFrame(
            promos,
            columns=["ID promotora", "Promotora", "Distritos (grupos)", "Total de grupos"],
        ) if promos else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar resumen de promotoras: {e}")
        df_promotoras = pd.DataFrame()

    # ------------------------------------------------------------------
    # 3) Resumen por DISTRITO (usa Id_Directiva para contar directivas)
    # ------------------------------------------------------------------
    try:
        cursor.execute(
            """
            SELECT d.Id_Distrito,
                   d.Nombre_distrito,
                   COUNT(DISTINCT g.Id_Grupo)      AS Total_grupos,
                   COUNT(DISTINCT g.Id_Promotora)  AS Total_promotoras,
                   COUNT(DISTINCT g.Id_Directiva)  AS Total_directivas
            FROM Distrito d
            LEFT JOIN Grupo g ON g.Id_Distrito = d.Id_Distrito
            GROUP BY d.Id_Distrito, d.Nombre_distrito
            ORDER BY d.Id_Distrito ASC
            """
        )
        dist = cursor.fetchall()
        df_distritos = pd.DataFrame(
            dist,
            columns=[
                "ID distrito",
                "Distrito",
                "Grupos",
                "Promotoras",
                "Directivas",
            ],
        ) if dist else pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar resumen de distritos: {e}")
        df_distritos = pd.DataFrame()

    cursor.close()
    con.close()

    # ------------------------------------------------------------------
    # 4) Tabs de visualización
    # ------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["🔹 Por grupo", "🔹 Por promotora", "🔹 Por distrito"])

    # ---- TAB 1: POR GRUPO ----
    with tab1:
        st.subheader("🔍 Buscar información por grupo")

        if df_grupos.empty:
            st.info("No hay grupos registrados.")
        else:
            nombres_grupo = ["(Todos)"] + df_grupos["Nombre de grupo"].unique().tolist()
            grupo_sel = st.selectbox("Seleccionar grupo", nombres_grupo)

            if grupo_sel != "(Todos)":
                df_filtrado = df_grupos[df_grupos["Nombre de grupo"] == grupo_sel]
            else:
                df_filtrado = df_grupos

            st.dataframe(df_filtrado, use_container_width=True)

    # ---- TAB 2: POR PROMOTORA ----
    with tab2:
        st.subheader("👩‍💼 Promotoras y sus grupos")

        if df_promotoras.empty:
            st.info("No hay promotoras registradas.")
        else:
            nombres_prom = ["(Todas)"] + df_promotoras["Promotora"].tolist()
            promotora_sel = st.selectbox("Seleccionar promotora", nombres_prom)

            if promotora_sel != "(Todas)":
                df_promo_filtrado = df_promotoras[
                    df_promotoras["Promotora"] == promotora_sel
                ]
                st.markdown("**Resumen de la promotora seleccionada:**")
                st.dataframe(df_promo_filtrado, use_container_width=True)

                if not df_grupos.empty:
                    st.markdown("**Grupos que lleva esta promotora:**")
                    df_grupos_promo = df_grupos[
                        df_grupos["Promotora"] == promotora_sel
                    ]
                    st.dataframe(df_grupos_promo, use_container_width=True)
            else:
                st.dataframe(df_promotoras, use_container_width=True)

    # ---- TAB 3: POR DISTRITO ----
    with tab3:
        st.subheader("🏙 Resumen por distrito")

        if df_distritos.empty:
            st.info("No hay distritos registrados.")
        else:
            distrito_sel = st.selectbox(
                "Seleccionar distrito",
                ["(Todos)"] + df_distritos["Distrito"].tolist(),
            )

            if distrito_sel != "(Todos)":
                df_dist_filtrado = df_distritos[df_distritos["Distrito"] == distrito_sel]
                st.markdown("**Resumen del distrito seleccionado:**")
                st.dataframe(df_dist_filtrado, use_container_width=True)

                if not df_grupos.empty:
                    st.markdown("**Grupos en este distrito:**")
                    df_grupos_dist = df_grupos[df_grupos["Distrito"] == distrito_sel]
                    st.dataframe(df_grupos_dist, use_container_width=True)
            else:
                st.dataframe(df_distritos, use_container_width=True)

import mysql.connector
from modulos.conexion import obtener_conexion

def ejecutar_reset_total():
    con = obtener_conexion()
    cursor = con.cursor()

    print("⏳ Reiniciando toda la base de datos CVX…")

    # ---------------------------------------------------------
    # 1. ELIMINAR TODAS LAS TABLAS (orden correcto)
    # ---------------------------------------------------------
    tablas = [
        "caja_movimientos",
        "caja_reunion",
        "caja_general",
        "Cuotas_prestamo",
        "Prestamo",
        "Ahorro",
        "Multa",
        "Tipo_de_multa",
        "Asistencia",
        "Reunion",
        "Gastos_grupo",
        "Socia",
        "Usuario"
    ]

    for t in tablas:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {t}")
            print(f"✔ Tabla {t} eliminada")
        except:
            print(f"⚠ No se pudo eliminar {t}")

    # ---------------------------------------------------------
    # 2. RECREAR TABLAS DESDE CERO
    # ---------------------------------------------------------

    # ---------- SOCIA ----------
    cursor.execute("""
        CREATE TABLE Socia (
            Id_Socia INT PRIMARY KEY AUTO_INCREMENT,
            Nombre VARCHAR(100),
            DUI VARCHAR(15),
            Telefono VARCHAR(15),
            Sexo VARCHAR(5)
        );
    """)

    # ---------- USUARIO ----------
    cursor.execute("""
        CREATE TABLE Usuario (
            Id_Usuario INT PRIMARY KEY AUTO_INCREMENT,
            Nombre VARCHAR(100),
            Usuario VARCHAR(50),
            Contrasena VARCHAR(255),
            Rol VARCHAR(20)
        );
    """)

    # ---------- REUNIÓN ----------
    cursor.execute("""
        CREATE TABLE Reunion (
            Id_Reunion INT PRIMARY KEY AUTO_INCREMENT,
            Fecha_reunion DATE,
            Observaciones TEXT,
            Acuerdos TEXT,
            Tema_central TEXT,
            Id_Grupo INT
        );
    """)

    # ---------- ASISTENCIA ----------
    cursor.execute("""
        CREATE TABLE Asistencia (
            Id_Asistencia INT PRIMARY KEY AUTO_INCREMENT,
            Id_Reunion INT,
            Id_Socia INT,
            Estado_asistencia VARCHAR(20),
            Fecha DATE
        );
    """)

    # ---------- TIPO DE MULTA ----------
    cursor.execute("""
        CREATE TABLE Tipo_de_multa (
            Id_Tipo_multa INT PRIMARY KEY AUTO_INCREMENT,
            `Tipo de multa` VARCHAR(100)
        );
    """)

    # ---------- MULTA ----------
    cursor.execute("""
        CREATE TABLE Multa (
            Id_Multa INT PRIMARY KEY AUTO_INCREMENT,
            Monto DECIMAL(10,2),
            Fecha_aplicacion DATE,
            Estado VARCHAR(20),
            Id_Tipo_multa INT,
            Id_Socia INT
        );
    """)

    # ---------- AHORRO ----------
    cursor.execute("""
        CREATE TABLE Ahorro (
            Id_Ahorro INT PRIMARY KEY AUTO_INCREMENT,
            `Fecha del aporte` DATE,
            `Monto del aporte` DECIMAL(10,2),
            `Tipo de aporte` VARCHAR(50),
            `Comprobante digital` VARCHAR(255),
            `Saldo acumulado` DECIMAL(10,2),
            Id_Socia INT
        );
    """)

    # ---------- PRESTAMO ----------
    cursor.execute("""
        CREATE TABLE Prestamo (
            Id_Prestamo INT PRIMARY KEY AUTO_INCREMENT,
            `Fecha del préstamo` DATE,
            `Monto prestado` DECIMAL(10,2),
            `Interes_total` DECIMAL(10,2),
            `Tasa de interes` DECIMAL(10,2),
            `Plazo` INT,
            `Cuotas` INT,
            `Saldo pendiente` DECIMAL(10,2),
            Estado_del_prestamo VARCHAR(20),
            Id_Grupo INT,
            Id_Socia INT,
            Id_Caja INT
        );
    """)

    # ---------- CUOTAS ----------
    cursor.execute("""
        CREATE TABLE Cuotas_prestamo (
            Id_Cuota INT PRIMARY KEY AUTO_INCREMENT,
            Id_Prestamo INT,
            Numero_cuota INT,
            Fecha_programada DATE,
            Monto_cuota DECIMAL(10,2),
            Estado VARCHAR(20),
            Id_Caja INT
        );
    """)

    # ---------- GASTOS DEL GRUPO ----------
    cursor.execute("""
        CREATE TABLE Gastos_grupo (
            Id_Gasto INT PRIMARY KEY AUTO_INCREMENT,
            Fecha_gasto DATE,
            Descripcion TEXT,
            Monto DECIMAL(10,2),
            Responsable VARCHAR(100),
            DUI VARCHAR(15),
            Id_Caja INT
        );
    """)

    # ---------- CAJA GENERAL (ÚNICA) ----------
    cursor.execute("""
        CREATE TABLE caja_general (
            id INT PRIMARY KEY,
            saldo_actual DECIMAL(10,2)
        );
    """)

    # Insertar saldo inicial $0.00
    cursor.execute("INSERT INTO caja_general (id, saldo_actual) VALUES (1, 0.00)")

    # ---------- CAJA REUNIÓN (REPORTE DIARIO) ----------
    cursor.execute("""
        CREATE TABLE caja_reunion (
            id_caja INT PRIMARY KEY AUTO_INCREMENT,
            fecha DATE,
            saldo_inicial DECIMAL(10,2),
            ingresos DECIMAL(10,2),
            egresos DECIMAL(10,2),
            saldo_final DECIMAL(10,2)
        );
    """)

    # ---------- MOVIMIENTOS ----------
    cursor.execute("""
        CREATE TABLE caja_movimientos (
            id_mov INT PRIMARY KEY AUTO_INCREMENT,
            id_caja INT,
            tipo VARCHAR(20),
            categoria VARCHAR(200),
            monto DECIMAL(10,2)
        );
    """)

    con.commit()
    cursor.close()
    con.close()

    print("✅ Reset total completado. Base de datos limpia lista para pruebas.")


# ================================================================
# EJECUCIÓN DIRECTA
# ================================================================
if __name__ == "__main__":
    ejecutar_reset_total()

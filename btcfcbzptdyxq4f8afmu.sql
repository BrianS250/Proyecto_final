-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: btcfcbzptdyxq4f8afmu-mysql.services.clever-cloud.com:3306
-- Tiempo de generación: 15-11-2025 a las 17:27:56
-- Versión del servidor: 8.0.22-13
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `btcfcbzptdyxq4f8afmu`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Acta`
--

CREATE TABLE `Acta` (
  `Id_Acta` int NOT NULL,
  `Contenido` text NOT NULL,
  `Fecha_creacion` date NOT NULL,
  `Tipo_acta` text NOT NULL,
  `Id_Reunión` int NOT NULL,
  `Id_Grupo` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Administrador`
--

CREATE TABLE `Administrador` (
  `Id_Administrador` int NOT NULL,
  `Nombre` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Ahorro`
--

CREATE TABLE `Ahorro` (
  `Id_Ahorro` int NOT NULL,
  `Fecha del aporte` date NOT NULL,
  `Monto del aporte` int NOT NULL,
  `Tipo de aporte` varchar(30) NOT NULL,
  `Comprobante digital` varchar(30) NOT NULL,
  `Saldo acumulado` int NOT NULL,
  `Id_Usuario` int NOT NULL,
  `Id_Reunión` int NOT NULL,
  `Id_Grupo` int NOT NULL,
  `Id_Caja` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Asistencia`
--

CREATE TABLE `Asistencia` (
  `Id_Asistencia` int NOT NULL,
  `Estado_asistencia` varchar(10) NOT NULL,
  `Multa_generada` int NOT NULL,
  `Id_Reunion` int NOT NULL,
  `Id_Usuario` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Caja`
--

CREATE TABLE `Caja` (
  `Id_Caja` int NOT NULL,
  `Concepto` text NOT NULL,
  `Monto` int NOT NULL,
  `Saldo_actual` int NOT NULL,
  `Id_Grupo` int NOT NULL,
  `Id_Tipo_movimiento` int NOT NULL,
  `Id_Multa` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Ciclo`
--

CREATE TABLE `Ciclo` (
  `Id_Ciclo` int NOT NULL,
  `Fecha_inicio` date NOT NULL,
  `Fecha_cierre` date NOT NULL,
  `Utilidades_ciclo` int NOT NULL,
  `Estado` text NOT NULL,
  `Id_Grupo` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Distrito`
--

CREATE TABLE `Distrito` (
  `Id_Distrito` int NOT NULL,
  `Nombre del distrito` text NOT NULL,
  `Representantes` int NOT NULL,
  `Cantidad de grupos` int NOT NULL,
  `Estado del distrito` text NOT NULL,
  `Id_Promotora` int NOT NULL,
  `Id_Administrador` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Grupo`
--

CREATE TABLE `Grupo` (
  `Id_Grupo` int NOT NULL,
  `Nombre_grupo` varchar(50) NOT NULL,
  `Tasa_de_interes` decimal(10,0) NOT NULL,
  `Periodicidad_de_reuniones` date NOT NULL,
  `Tipo_de_multa` varchar(50) NOT NULL,
  `Reglas_de_prestamo` text NOT NULL,
  `fecha_inicio` date NOT NULL,
  `Id_Promotora` int NOT NULL,
  `Id_Distrito` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Multa`
--

CREATE TABLE `Multa` (
  `Id_Multa` int NOT NULL,
  `Monto` int NOT NULL,
  `Fecha_aplicacion` date NOT NULL,
  `Estado` text NOT NULL,
  `Id_Tipo_multa` int NOT NULL,
  `Id_Usuario` int NOT NULL,
  `Id_Asistencia` int NOT NULL,
  `Id_Préstamo` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Pago del préstamo`
--

CREATE TABLE `Pago del préstamo` (
  `Id_Pago` int NOT NULL,
  `Fecha de pago` date NOT NULL,
  `Monto abonado` int NOT NULL,
  `Interés pagado` int NOT NULL,
  `Capital pagado` int NOT NULL,
  `Saldo restante` int NOT NULL,
  `Id_Préstamo` int NOT NULL,
  `Id_Caja` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Promotora`
--

CREATE TABLE `Promotora` (
  `Id_Promotora` int NOT NULL,
  `Nombre` text NOT NULL,
  `Distrito` text NOT NULL,
  `Correo` varchar(40) NOT NULL,
  `Contacto` int NOT NULL,
  `Cantidad de grupos asignados` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Préstamo`
--

CREATE TABLE `Préstamo` (
  `Id_Préstamo` int NOT NULL,
  `Fecha del préstamo` date NOT NULL,
  `Monto prestado` int NOT NULL,
  `Tasa de interes` int NOT NULL,
  `Plazo` int NOT NULL,
  `Cuotas` int NOT NULL,
  `Saldo pendiente` int NOT NULL,
  `Estado del préstamo` text NOT NULL,
  `Id_Grupo` int NOT NULL,
  `Id_Usuario` int NOT NULL,
  `Id_Caja` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Reunion`
--

CREATE TABLE `Reunion` (
  `Id_Reunion` int NOT NULL,
  `Fecha_reunion` date NOT NULL,
  `observaciones` text NOT NULL,
  `Acuerdos` mediumtext NOT NULL,
  `Tema_central` varchar(50) NOT NULL,
  `Id_Grupo` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Roles`
--

CREATE TABLE `Roles` (
  `Id_Roles` int NOT NULL,
  `Tipo_de_rol` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Tipo de movimiento`
--

CREATE TABLE `Tipo de movimiento` (
  `Id_Tipo_movimiento` int NOT NULL,
  `Ingreso` varchar(30) NOT NULL,
  `Egreso` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Tipo de multa`
--

CREATE TABLE `Tipo de multa` (
  `Id_Tipo_multa` int NOT NULL,
  `Tipo de multa` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `Usuario`
--

CREATE TABLE `Usuario` (
  `Id_Usuario` int NOT NULL,
  `Nombre` varchar(50) NOT NULL,
  `Id_Grupo` int NOT NULL,
  `Id_Roles` int NOT NULL,
  `Telefono` varchar(30) NOT NULL,
  `Correo` varchar(255) NOT NULL,
  `Estado_usuario` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `Acta`
--
ALTER TABLE `Acta`
  ADD PRIMARY KEY (`Id_Acta`),
  ADD UNIQUE KEY `Id_Reunión` (`Id_Reunión`),
  ADD UNIQUE KEY `Id_Grupo` (`Id_Grupo`);

--
-- Indices de la tabla `Administrador`
--
ALTER TABLE `Administrador`
  ADD PRIMARY KEY (`Id_Administrador`);

--
-- Indices de la tabla `Ahorro`
--
ALTER TABLE `Ahorro`
  ADD PRIMARY KEY (`Id_Ahorro`),
  ADD UNIQUE KEY `Id_Usuario` (`Id_Usuario`),
  ADD UNIQUE KEY `Id_Reunión` (`Id_Reunión`),
  ADD UNIQUE KEY `Id_Grupo` (`Id_Grupo`),
  ADD UNIQUE KEY `Id_Caja` (`Id_Caja`);

--
-- Indices de la tabla `Asistencia`
--
ALTER TABLE `Asistencia`
  ADD PRIMARY KEY (`Id_Asistencia`),
  ADD UNIQUE KEY `Id_Reunion` (`Id_Reunion`),
  ADD UNIQUE KEY `Id_Usuario` (`Id_Usuario`);

--
-- Indices de la tabla `Caja`
--
ALTER TABLE `Caja`
  ADD PRIMARY KEY (`Id_Caja`),
  ADD UNIQUE KEY `Id_Grupo` (`Id_Grupo`),
  ADD UNIQUE KEY `Id_Tipo_movimiento` (`Id_Tipo_movimiento`),
  ADD UNIQUE KEY `Id_Multa` (`Id_Multa`);

--
-- Indices de la tabla `Ciclo`
--
ALTER TABLE `Ciclo`
  ADD PRIMARY KEY (`Id_Ciclo`),
  ADD UNIQUE KEY `Id_Grupo` (`Id_Grupo`);

--
-- Indices de la tabla `Distrito`
--
ALTER TABLE `Distrito`
  ADD PRIMARY KEY (`Id_Distrito`),
  ADD UNIQUE KEY `Id_Promotora` (`Id_Promotora`),
  ADD UNIQUE KEY `Id_Administrador` (`Id_Administrador`);

--
-- Indices de la tabla `Grupo`
--
ALTER TABLE `Grupo`
  ADD PRIMARY KEY (`Id_Grupo`),
  ADD UNIQUE KEY `Id_Promotora` (`Id_Promotora`),
  ADD UNIQUE KEY `Id_Distrito` (`Id_Distrito`);

--
-- Indices de la tabla `Multa`
--
ALTER TABLE `Multa`
  ADD PRIMARY KEY (`Id_Multa`),
  ADD UNIQUE KEY `Id_Tipo_multa` (`Id_Tipo_multa`),
  ADD UNIQUE KEY `Id_Usuario` (`Id_Usuario`),
  ADD UNIQUE KEY `Id_Asistencia` (`Id_Asistencia`),
  ADD UNIQUE KEY `Id_Préstamo` (`Id_Préstamo`);

--
-- Indices de la tabla `Pago del préstamo`
--
ALTER TABLE `Pago del préstamo`
  ADD PRIMARY KEY (`Id_Pago`),
  ADD UNIQUE KEY `Id_Préstamo` (`Id_Préstamo`),
  ADD UNIQUE KEY `Id_Caja` (`Id_Caja`);

--
-- Indices de la tabla `Promotora`
--
ALTER TABLE `Promotora`
  ADD PRIMARY KEY (`Id_Promotora`);

--
-- Indices de la tabla `Préstamo`
--
ALTER TABLE `Préstamo`
  ADD PRIMARY KEY (`Id_Préstamo`),
  ADD UNIQUE KEY `Id_Grupo` (`Id_Grupo`),
  ADD UNIQUE KEY `Id_Usuario` (`Id_Usuario`),
  ADD UNIQUE KEY `Id_Caja` (`Id_Caja`);

--
-- Indices de la tabla `Reunion`
--
ALTER TABLE `Reunion`
  ADD PRIMARY KEY (`Id_Reunion`),
  ADD UNIQUE KEY `id_Grupo` (`Id_Grupo`);

--
-- Indices de la tabla `Roles`
--
ALTER TABLE `Roles`
  ADD PRIMARY KEY (`Id_Roles`);

--
-- Indices de la tabla `Tipo de movimiento`
--
ALTER TABLE `Tipo de movimiento`
  ADD PRIMARY KEY (`Id_Tipo_movimiento`);

--
-- Indices de la tabla `Tipo de multa`
--
ALTER TABLE `Tipo de multa`
  ADD PRIMARY KEY (`Id_Tipo_multa`);

--
-- Indices de la tabla `Usuario`
--
ALTER TABLE `Usuario`
  ADD PRIMARY KEY (`Id_Usuario`),
  ADD UNIQUE KEY `id_Grupo` (`Id_Grupo`),
  ADD UNIQUE KEY `id_Roles` (`Id_Roles`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `Acta`
--
ALTER TABLE `Acta`
  MODIFY `Id_Acta` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Administrador`
--
ALTER TABLE `Administrador`
  MODIFY `Id_Administrador` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Ahorro`
--
ALTER TABLE `Ahorro`
  MODIFY `Id_Ahorro` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Asistencia`
--
ALTER TABLE `Asistencia`
  MODIFY `Id_Asistencia` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Caja`
--
ALTER TABLE `Caja`
  MODIFY `Id_Caja` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Ciclo`
--
ALTER TABLE `Ciclo`
  MODIFY `Id_Ciclo` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Distrito`
--
ALTER TABLE `Distrito`
  MODIFY `Id_Distrito` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Grupo`
--
ALTER TABLE `Grupo`
  MODIFY `Id_Grupo` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Multa`
--
ALTER TABLE `Multa`
  MODIFY `Id_Multa` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Pago del préstamo`
--
ALTER TABLE `Pago del préstamo`
  MODIFY `Id_Pago` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Promotora`
--
ALTER TABLE `Promotora`
  MODIFY `Id_Promotora` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Préstamo`
--
ALTER TABLE `Préstamo`
  MODIFY `Id_Préstamo` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Reunion`
--
ALTER TABLE `Reunion`
  MODIFY `Id_Reunion` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Roles`
--
ALTER TABLE `Roles`
  MODIFY `Id_Roles` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Tipo de movimiento`
--
ALTER TABLE `Tipo de movimiento`
  MODIFY `Id_Tipo_movimiento` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Tipo de multa`
--
ALTER TABLE `Tipo de multa`
  MODIFY `Id_Tipo_multa` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `Usuario`
--
ALTER TABLE `Usuario`
  MODIFY `Id_Usuario` int NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `Préstamo`
--
ALTER TABLE `Préstamo`
  ADD CONSTRAINT `Préstamo_ibfk_1` FOREIGN KEY (`Id_Usuario`) REFERENCES `Usuario` (`Id_Usuario`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

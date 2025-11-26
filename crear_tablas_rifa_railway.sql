-- ============================================
-- SCRIPT PARA CREAR TABLAS DE RIFA EN RAILWAY
-- Fecha: 2025-11-05
-- Base de datos: railway
-- ============================================

USE railway;

-- ============================================
-- TABLA: rifa
-- Descripción: Almacena información de rifas
-- ============================================
CREATE TABLE IF NOT EXISTS `rifa` (
  `id_rifa` INT AUTO_INCREMENT PRIMARY KEY,
  `uuid_rifa` VARCHAR(36) NOT NULL UNIQUE,
  `nombre` VARCHAR(255) NOT NULL COMMENT 'Nombre de la rifa (ej: RIFA 2026)',
  `descripcion` TEXT COMMENT 'Descripción de la rifa',
  `fecha_inicio` DATETIME NOT NULL COMMENT 'Fecha de inicio de la rifa',
  `fecha_fin` DATETIME NOT NULL COMMENT 'Fecha límite para participar',
  `fecha_sorteo` DATETIME NOT NULL COMMENT 'Fecha y hora del sorteo',
  `total_premios` INT DEFAULT 10 COMMENT 'Número total de premios',
  `monto_por_boleto` DECIMAL(10,2) DEFAULT 100.00 COMMENT 'Monto de compra para obtener 1 boleto',
  `estado` ENUM('activa', 'finalizada', 'cancelada') DEFAULT 'activa',
  `uuid_sucursal` VARCHAR(36) COMMENT 'Sucursal responsable',
  `transmision_url` VARCHAR(500) COMMENT 'URL de transmisión en vivo',
  `imagen_banner` VARCHAR(255) COMMENT 'Ruta de imagen del banner',
  `is_active` TINYINT(1) DEFAULT 1,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_uuid_rifa` (`uuid_rifa`),
  INDEX `idx_fecha_sorteo` (`fecha_sorteo`),
  INDEX `idx_estado` (`estado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tabla principal de rifas';

-- ============================================
-- TABLA: rifa_boleto
-- Descripción: Almacena los boletos generados
-- ============================================
CREATE TABLE IF NOT EXISTS `rifa_boleto` (
  `id_boleto` INT AUTO_INCREMENT PRIMARY KEY,
  `uuid_boleto` VARCHAR(36) NOT NULL UNIQUE,
  `uuid_rifa` VARCHAR(36) NOT NULL COMMENT 'Referencia a la rifa',
  `folio_boleto` VARCHAR(50) NOT NULL UNIQUE COMMENT 'Número de boleto único',
  `uuid_cliente` VARCHAR(36) COMMENT 'Cliente dueño del boleto',
  `nombre_cliente` VARCHAR(255) COMMENT 'Nombre del cliente',
  `telefono_cliente` VARCHAR(20) COMMENT 'Teléfono del cliente',
  `tipo_obtencion` ENUM('compra', 'referido', 'manual') DEFAULT 'compra' COMMENT 'Cómo se obtuvo el boleto',
  `monto_compra` DECIMAL(10,2) COMMENT 'Monto de la compra que generó el boleto',
  `uuid_venta` VARCHAR(36) COMMENT 'Referencia a la venta que generó el boleto',
  `folio_venta` VARCHAR(50) COMMENT 'Folio de la venta',
  `referido_por` VARCHAR(36) COMMENT 'UUID del cliente que refirió',
  `es_ganador` TINYINT(1) DEFAULT 0 COMMENT 'Si este boleto es ganador',
  `numero_premio` INT COMMENT 'Número del premio ganado (1-10)',
  `descripcion_premio` VARCHAR(500) COMMENT 'Descripción del premio ganado',
  `fecha_generacion` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Cuándo se generó el boleto',
  `fecha_sorteo_ganador` DATETIME COMMENT 'Cuándo fue sorteado como ganador',
  `estado` ENUM('activo', 'canjeado', 'anulado') DEFAULT 'activo',
  `is_active` TINYINT(1) DEFAULT 1,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_uuid_boleto` (`uuid_boleto`),
  INDEX `idx_uuid_rifa` (`uuid_rifa`),
  INDEX `idx_folio_boleto` (`folio_boleto`),
  INDEX `idx_uuid_cliente` (`uuid_cliente`),
  INDEX `idx_es_ganador` (`es_ganador`),
  INDEX `idx_tipo_obtencion` (`tipo_obtencion`),
  INDEX `idx_fecha_generacion` (`fecha_generacion`),
  FOREIGN KEY (`uuid_rifa`) REFERENCES `rifa`(`uuid_rifa`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Boletos generados para las rifas';

-- ============================================
-- TABLA: rifa_premio
-- Descripción: Detalles de los premios
-- ============================================
CREATE TABLE IF NOT EXISTS `rifa_premio` (
  `id_premio` INT AUTO_INCREMENT PRIMARY KEY,
  `uuid_premio` VARCHAR(36) NOT NULL UNIQUE,
  `uuid_rifa` VARCHAR(36) NOT NULL COMMENT 'Referencia a la rifa',
  `numero_premio` INT NOT NULL COMMENT 'Orden del premio (1 = primer lugar)',
  `nombre_premio` VARCHAR(255) NOT NULL COMMENT 'Nombre del premio',
  `descripcion` TEXT COMMENT 'Descripción detallada',
  `valor_estimado` DECIMAL(10,2) COMMENT 'Valor estimado del premio',
  `imagen` VARCHAR(255) COMMENT 'Imagen del premio',
  `uuid_boleto_ganador` VARCHAR(36) COMMENT 'Boleto que ganó este premio',
  `estado` ENUM('disponible', 'sorteado', 'entregado') DEFAULT 'disponible',
  `is_active` TINYINT(1) DEFAULT 1,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_uuid_premio` (`uuid_premio`),
  INDEX `idx_uuid_rifa` (`uuid_rifa`),
  INDEX `idx_numero_premio` (`numero_premio`),
  FOREIGN KEY (`uuid_rifa`) REFERENCES `rifa`(`uuid_rifa`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Premios de las rifas';

-- ============================================
-- INSERTAR RIFA 2026 (DATOS INICIALES)
-- ============================================
INSERT INTO `rifa` (
  `uuid_rifa`,
  `nombre`,
  `descripcion`,
  `fecha_inicio`,
  `fecha_fin`,
  `fecha_sorteo`,
  `total_premios`,
  `monto_por_boleto`,
  `estado`,
  `uuid_sucursal`,
  `transmision_url`,
  `is_active`
) VALUES (
  UUID(),
  'RIFA 2026',
  'Cada compra te acerca a ganar increíbles premios. Por cada $100 MXN de compra recibes 1 boleto automático.',
  '2025-09-30 00:00:00',
  '2026-01-15 23:59:59',
  '2026-01-16 21:00:00',
  10,
  100.00,
  'activa',
  '22C8131D-4431-4E9A-AA04-ED188217C549',
  'https://www.facebook.com/share/1Cqyydwaas/',
  1
) ON DUPLICATE KEY UPDATE
  `descripcion` = VALUES(`descripcion`),
  `transmision_url` = VALUES(`transmision_url`);

-- ============================================
-- INSERTAR PREMIOS PARA RIFA 2026
-- ============================================
SET @uuid_rifa_2026 = (SELECT uuid_rifa FROM rifa WHERE nombre = 'RIFA 2026' AND is_active = 1 LIMIT 1);

INSERT INTO `rifa_premio` (
  `uuid_premio`,
  `uuid_rifa`,
  `numero_premio`,
  `nombre_premio`,
  `descripcion`,
  `estado`,
  `is_active`
) VALUES 
  (UUID(), @uuid_rifa_2026, 1, 'Primer Lugar', 'Premio principal por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 2, 'Segundo Lugar', 'Premio por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 3, 'Tercer Lugar', 'Premio por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 4, 'Cuarto Lugar', 'Premio por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 5, 'Quinto Lugar', 'Premio por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 6, 'Sexto Lugar', 'Premio por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 7, 'Séptimo Lugar', 'Premio por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 8, 'Octavo Lugar', 'Premio por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 9, 'Noveno Lugar', 'Premio por anunciar', 'disponible', 1),
  (UUID(), @uuid_rifa_2026, 10, 'Décimo Lugar', 'Premio por anunciar', 'disponible', 1)
ON DUPLICATE KEY UPDATE
  `descripcion` = VALUES(`descripcion`);

-- ============================================
-- VERIFICACIÓN
-- ============================================
SELECT 'Tablas creadas exitosamente' AS mensaje;
SELECT COUNT(*) AS total_rifas FROM rifa WHERE is_active = 1;
SELECT COUNT(*) AS total_premios FROM rifa_premio WHERE is_active = 1;

-- ============================================
-- FIN DEL SCRIPT
-- ============================================

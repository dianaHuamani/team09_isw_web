CREATE DATABASE IF NOT EXISTS farmacia_inkafarma
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE farmacia_inkafarma;

CREATE TABLE IF NOT EXISTS categories (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(80) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO categories (name) VALUES
('Analgésicos'), ('Antisépticos'), ('Dermocosmética'),
('Vitaminas'), ('General');

CREATE TABLE IF NOT EXISTS products (
  id INT NOT NULL AUTO_INCREMENT,
  sku VARCHAR(32) NOT NULL,
  name VARCHAR(140) NOT NULL,
  category_id INT NOT NULL,
  presentation VARCHAR(80) NOT NULL DEFAULT 'Unidad',
  stock INT NOT NULL DEFAULT 0,
  min_stock INT NOT NULL DEFAULT 5,
  price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
  expiry_date DATE NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_products_sku (sku),
  KEY ix_products_name (name),
  KEY ix_products_category (category_id),
  CONSTRAINT fk_products_category FOREIGN KEY (category_id)
    REFERENCES categories(id) ON UPDATE CASCADE ON DELETE RESTRICT,
  CONSTRAINT chk_products_stock_nonnegative CHECK (stock >= 0),
  CONSTRAINT chk_products_min_stock_nonnegative CHECK (min_stock >= 0),
  CONSTRAINT chk_products_price_nonnegative CHECK (price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS appointments (
  id INT NOT NULL AUTO_INCREMENT,
  patient_name VARCHAR(140) NOT NULL,
  phone VARCHAR(30) NOT NULL,
  service VARCHAR(100) NOT NULL,
  professional VARCHAR(100) NOT NULL DEFAULT 'Por asignar',
  appointment_at DATETIME NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'Programada',
  notes VARCHAR(300) NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_appointments_appointment_at (appointment_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contact_messages (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(160) NOT NULL,
  phone VARCHAR(30) NULL,
  subject VARCHAR(140) NOT NULL,
  message TEXT NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'Pendiente',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO products
(sku, name, category_id, presentation, stock, min_stock, price)
SELECT 'DEM-001', 'Paracetamol 500 mg', id, 'Caja x 100 tabletas', 50, 10, 12.50
FROM categories WHERE name = 'Analgésicos';
INSERT IGNORE INTO products
(sku, name, category_id, presentation, stock, min_stock, price)
SELECT 'DEM-002', 'Alcohol Medicinal 70°', id, 'Frasco x 120 ml', 40, 10, 4.50
FROM categories WHERE name = 'Antisépticos';
INSERT IGNORE INTO products
(sku, name, category_id, presentation, stock, min_stock, price)
SELECT 'DEM-003', 'Protector Solar FPS 50', id, 'Frasco x 50 ml', 25, 5, 65.00
FROM categories WHERE name = 'Dermocosmética';
INSERT IGNORE INTO products
(sku, name, category_id, presentation, stock, min_stock, price)
SELECT 'DEM-004', 'Vitamina C 500 mg', id, 'Frasco x 60 tabletas', 35, 8, 28.90
FROM categories WHERE name = 'Vitaminas';

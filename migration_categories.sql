-- Ejecutar UNA SOLA VEZ sobre la base existente farmacia_inkafarma
-- usando el usuario administrador de RDS, nunca app_web/app_desktop.
USE farmacia_inkafarma;

CREATE TABLE IF NOT EXISTS categories (
  id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(80) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_categories_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO categories (name)
SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category <> '';

ALTER TABLE products ADD COLUMN category_id INT NULL;

UPDATE products p
JOIN categories c ON c.name = p.category
SET p.category_id = c.id;

INSERT IGNORE INTO categories (name) VALUES ('General');
UPDATE products
SET category_id = (SELECT id FROM categories WHERE name = 'General')
WHERE category_id IS NULL;

ALTER TABLE products MODIFY category_id INT NOT NULL;
ALTER TABLE products ADD INDEX ix_products_category (category_id);
ALTER TABLE products ADD CONSTRAINT fk_products_category
  FOREIGN KEY (category_id) REFERENCES categories(id)
  ON UPDATE CASCADE ON DELETE RESTRICT;

-- La columna category anterior deja de utilizarse por la aplicación.
ALTER TABLE products DROP COLUMN category;

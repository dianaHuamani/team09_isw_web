-- Ejecutar en RDS con el usuario administrador.
-- Reemplaza las contraseñas de ejemplo antes de ejecutar.
CREATE USER IF NOT EXISTS 'app_web'@'%' IDENTIFIED BY 'REEMPLAZAR_CLAVE_WEB';
GRANT SELECT, INSERT, UPDATE, DELETE
ON farmacia_inkafarma.* TO 'app_web'@'%';

CREATE USER IF NOT EXISTS 'app_desktop'@'%' IDENTIFIED BY 'REEMPLAZAR_CLAVE_DESKTOP';
GRANT SELECT, INSERT, UPDATE, DELETE
ON farmacia_inkafarma.* TO 'app_desktop'@'%';

SHOW GRANTS FOR 'app_web'@'%';
SHOW GRANTS FOR 'app_desktop'@'%';

# Inkafarma · Sitio web informativo

Sitio público de presentación para una farmacia. Muestra información, un catálogo de productos de solo lectura, servicios, un formulario para contactar y una solicitud para agendar una cita médica.

## Lo que puede hacer el visitante

- Leer información general sobre la farmacia y sus servicios.
- Explorar, buscar y filtrar productos. Solo se muestran nombre, categoría, presentación y precio; no se muestran existencias ni datos internos del inventario.
- Enviar un mensaje desde **Contáctanos**.
- Enviar una solicitud de cita con un servicio y horario preferido. La farmacia debe confirmar la disponibilidad por teléfono.

El sitio **no permite crear, editar ni eliminar productos**, ni administrar inventario o revisar mensajes y citas. Esas tareas corresponden a un sistema interno separado. El catálogo consulta los productos del mismo esquema MySQL/SQLite; la aplicación pública solo tiene rutas de lectura para productos.

## Ejecutar en Windows / PowerShell

Requiere Python 3.10 o posterior.

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
py app.py
```

Abre `http://127.0.0.1:5000`. También puedes usar `py run.py`. Si no configuras RDS, los datos se guardan en SQLite local (`instance/farmacia.db`).

En el primer inicio con SQLite, la aplicación carga cuatro productos de demostración para que el catálogo muestre las imágenes incluidas en `app/static/img/`. No agrega datos de demostración a una base RDS.

## Conectar con AWS RDS

RDS permanece **privado**. Para ejecutar esta app desde tu PC, crea un túnel SSH por una instancia EC2 bastión que tenga acceso a la misma VPC que RDS. AWS también recomienda usar una bastión o VPN cuando necesitas llegar a una base privada desde fuera de la VPC.

### 1. Reglas de red

- En el grupo de seguridad de la EC2 bastión, permite SSH/TCP `22` desde tu IP pública.
- En el grupo de seguridad de RDS, permite MySQL/TCP `3306` con origen el **grupo de seguridad de la EC2 bastión**. No uses una regla abierta a Internet.
- La instancia EC2 necesita una dirección pública o una ruta SSH accesible desde tu PC. RDS se queda con **Public access: No**.

La EC2 y RDS deben tener conectividad de red dentro de la VPC (o por una conexión privada equivalente).

### 2. Abrir el túnel en Windows

En una primera ventana de PowerShell, reemplaza la ruta de la llave, el endpoint de RDS, el usuario SSH y la IP pública de la EC2:

```powershell
ssh -i "C:\ruta\a\mi-llave.pem" -N -L 3307:MI-ENDPOINT-RDS:3306 ec2-user@IP-PUBLICA-EC2
```

Usa `ec2-user` para Amazon Linux o el usuario configurado en tu instancia. Deja esa ventana abierta mientras uses la aplicación. El puerto local `3307` se reenvía por SSH al puerto `3306` de RDS.

### 3. Configurar el proyecto

En el `.env` del proyecto, usa la dirección local del túnel. La configuración de la app acepta estas variables y codifica el usuario y la contraseña al construir la URL de conexión:

```dotenv
DATABASE_URL=mysql+pymysql://USUARIO:CONTRASENA@127.0.0.1:3307/farmacia_inkafarma?charset=utf8mb4
FLASK_DEBUG=0
```

La URL usa `mysql+pymysql` porque ese es el conector instalado por `requirements.txt`. No dejes espacios alrededor del usuario, la contraseña, el host ni el puerto; si la contraseña contiene caracteres reservados de URL, codifícalos. No compartas `.env` ni lo subas a Git. En otra ventana de PowerShell, activa el entorno virtual y ejecuta `python app.py`. Mientras el túnel siga abierto, la app se conecta a la base privada. Si Workbench necesita conectarse desde tu PC, configura su host como `127.0.0.1` y su puerto como `3307` mientras el túnel está activo.

### 4. Crear las tablas

Con el túnel abierto, conecta MySQL Workbench a `127.0.0.1:3307` y ejecuta `schema.sql` una sola vez. El script crea las tablas y agrega cuatro productos de demostración. Si la base tiene otro nombre, cambia `CREATE DATABASE` y `USE` en el script y configura el mismo nombre en `DB_NAME`. El usuario MySQL necesita permisos para crear tablas durante esta preparación y para que la aplicación lea productos y guarde citas y mensajes.

Si ejecutas la aplicación en EC2 dentro de la VPC, no necesitas el túnel local. Usa el endpoint privado directamente en `DATABASE_URL`:

```dotenv
DATABASE_URL=mysql+pymysql://USUARIO:CONTRASENA@ENDPOINT-RDS:3306/farmacia_inkafarma?charset=utf8mb4
```

En el grupo de seguridad de RDS, permite MySQL/TCP `3306` desde el grupo de seguridad de esa EC2.

El sitio muestra productos registrados con stock mayor que cero y sin vencimiento pasado. Si el catálogo está vacío, carga los productos desde tu proceso administrativo separado.

## Estructura

```text
app/
  config.py          Configuración SQLite / RDS
  database.py        SQLAlchemy
  constants.py       Estados y servicios
  models/            Producto, cita y contacto
  routes/            Rutas públicas Flask
  services/          Catálogo, citas y contactos
  templates/         Sitio web con Jinja
  static/css/        Estilos adaptables
  static/js/         Menú móvil y avisos
app.py               Punto de entrada
Dockerfile           Imagen de despliegue
.python-version      Versión de Python
sitemap.xml          Rutas públicas para buscadores
schema.sql           Esquema de MySQL / RDS
```

## CRUD web de inventario

El módulo administrativo está disponible en `/admin/login`. Protege el acceso con
`ADMIN_USERNAME` y `ADMIN_PASSWORD` en el archivo `.env`. Después de iniciar sesión,
usa `/admin/productos` para registrar, listar, editar y eliminar medicamentos.

La aplicación web se conecta con el usuario MySQL `app_web`. Este usuario necesita
únicamente `SELECT`, `INSERT`, `UPDATE` y `DELETE` sobre `farmacia_inkafarma`.
No ejecutes `db.create_all()` en producción: las tablas se preparan por separado
con el usuario administrador mediante `schema.sql` (base nueva) o
`migration_categories.sql` (base existente). La aplicación ya no intenta crear
tablas al arrancar.

Para una base RDS existente que tenía `products.category` como texto, ejecuta
`migration_categories.sql` una sola vez desde MySQL Workbench con una conexión
administrativa. Para una base nueva, ejecuta `schema.sql` con el usuario
administrador. Después configura `.env` con `DB_HOST`, `DB_PORT`, `DB_USER=app_web`,
`DB_PASSWORD` y `DB_NAME=farmacia_inkafarma`.

El modelo ahora relaciona `products.category_id` con `categories.id` mediante
una llave foránea. Las categorías iniciales se insertan desde el script SQL.

## Antes de publicar

Esta es una base demostrativa. Configura los datos reales de contacto, dirección y horarios de cada tienda. Añade protección CSRF, límites contra spam, autenticación y permisos en el sistema administrativo separado, así como políticas de privacidad, respaldo y retención. No solicites diagnósticos ni guardes información clínica en los formularios. La marca y el contenido se deben revisar antes de presentar el sitio como un canal oficial.


### Configuración inicial del despliegue

1. En una base RDS nueva, ejecuta `schema.sql` con el usuario administrador.
   Si ya existe la tabla `products` con la columna `category` de texto, ejecuta
   en su lugar `migration_categories.sql` una sola vez con el usuario administrador.
2. Ejecuta `database_users.example.sql` después de reemplazar las contraseñas
   de ejemplo. Si los usuarios ya existen, no vuelvas a crear sus contraseñas:
   verifica sus permisos con `SHOW GRANTS`.
3. En EC2, crea el archivo `.env` a partir de `.env.example`. Usa el endpoint
   privado de RDS, `DB_USER=app_web` y la contraseña de ese usuario. Define también
   `SECRET_KEY`, `ADMIN_USERNAME` y `ADMIN_PASSWORD`.
4. Instala `requirements.txt` y reinicia el proceso Flask/Gunicorn.
5. Abre `http://IP-PUBLICA-EC2:5000/admin/login` para entrar al CRUD.

No compartas ni subas `.env`, `config.properties` ni llaves `.pem` al repositorio.
El ZIP contiene el código de la aplicación web Flask; la aplicación Java de
escritorio debe permanecer en su proyecto separado y conectarse a las mismas
tablas de RDS mediante `app_desktop`.

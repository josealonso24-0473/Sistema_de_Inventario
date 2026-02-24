# Sistema de Gestión de Inventario (Django)

Este proyecto implementa el sistema de gestión de inventario descrito en el documento **PRD — Sistema de Gestión de Inventario v1.0 · 2025**, usando **Python 3.11**, **Django 5.x** y **PostgreSQL/SQLite**.

## Estructura principal

- `manage.py` — Comando principal de Django.
- `config/` — Configuración global del proyecto.
  - `settings/base.py` — Configuración común.
  - `settings/development.py` — Configuración para desarrollo.
  - `settings/production.py` — Configuración para producción.
  - `urls.py` — URLs raíz.
  - `asgi.py` / `wsgi.py` — Puntos de entrada del servidor.
- `apps/` — Aplicaciones de negocio.
  - `accounts/` — Autenticación y sesiones.
  - `products/` — Productos, categorías, proveedores (Repository Pattern).
  - `inventory/` — Movimientos de stock y observadores (Observer Pattern).
  - `reports/` — Reportes y exportación a CSV.
- `templates/` — Plantillas HTML (Django Templates + Bootstrap 5).
- `static/` — Archivos estáticos (CSS, JS, imágenes).

## Instalación rápida

1. Crear y activar entorno virtual (recomendado):

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # o
   source venv/bin/activate  # Linux/Mac
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Crear archivo `.env` en la raíz del proyecto (mismo nivel que `manage.py`), basado en este ejemplo:

   ```env
   SECRET_KEY=una-clave-secreta-larga
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DATABASE_URL=sqlite:///db.sqlite3
   ```

4. Ejecutar migraciones y crear superusuario:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Iniciar el servidor de desarrollo:

   ```bash
   python manage.py runserver
   ```

   La configuración por defecto usa `config.settings.development`.

## Notas de arquitectura

- **Arquitectura en capas**:
  - Vista (Views) → Servicio (Services) → Repositorio (Repositories) → Base de Datos.
  - Las vistas no acceden al ORM directamente.
- **Repository Pattern**:
  - Implementado en `apps/products/repositories/`.
  - La lógica de negocio usa `ProductService`, que depende de una interfaz de repositorio.
- **Observer Pattern**:
  - Implementado en `apps/inventory/observers/`.
  - `InventoryService` notifica a los observadores tras cada movimiento de stock.

Este esqueleto está preparado para que añadas la lógica y las vistas finales siguiendo el PRD.


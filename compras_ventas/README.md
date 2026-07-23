# Mini sistema de Compras y Ventas (Django)

Sistema ligero con control de inventario:

- **Productos** con precio de venta.
- **Compras** (entradas) que suman stock.
- **Ventas** (salidas) que descuentan stock, con validación de existencias.
- **Dashboard** en `/` con inventario, totales y ganancia.
- **Panel de administración** en `/admin/` para todo el CRUD (viene gratis con Django).

El stock **se calcula** (compras − ventas), así nunca se descuadra el inventario.

## Ejecutar en local

```bash
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser        # crea tu usuario admin
python manage.py runserver
```

Abre http://127.0.0.1:8000/ (dashboard) y http://127.0.0.1:8000/admin/ (gestión).

## Desplegar en Azure App Service (Linux · Python)

1. **Crear el recurso**: App Service con runtime *Python 3.12* (Linux).

2. **Variables de aplicación** (App Service → *Configuración* → *Variables de entorno*):

   | Nombre           | Valor                                         |
   |------------------|-----------------------------------------------|
   | `SECRET_KEY`     | una cadena aleatoria larga                     |
   | `DEBUG`          | `0`                                            |
   | `DATABASE_URL`   | *(opcional)* `postgres://user:pass@host:5432/db` |

   Azure inyecta `WEBSITE_HOSTNAME` automáticamente; el proyecto ya lo añade a
   `ALLOWED_HOSTS` y a `CSRF_TRUSTED_ORIGINS`.

3. **Comando de inicio** (App Service → *Configuración* → *Comando de inicio*):

   ```
   startup.sh
   ```

   (Ya aplica migraciones, recopila estáticos y arranca gunicorn.)

4. **Desplegar el código** con cualquiera de estas opciones:

   ```bash
   # Opción A: ZIP deploy
   az webapp up --name MI-APP --runtime "PYTHON:3.12"

   # Opción B: Git / GitHub Actions / VS Code
   ```

   Oryx (el build de Azure) detecta `requirements.txt` e instala todo solo.

### Nota sobre la base de datos

Por defecto usa **SQLite**, ideal para probar. En Azure el disco es **efímero**:
los datos se pierden al reiniciar o redeployar. Para datos permanentes crea un
**Azure Database for PostgreSQL**, descomenta `psycopg[binary]` en
`requirements.txt` y define `DATABASE_URL`.

## Estructura

```
compras_ventas/
├── manage.py
├── requirements.txt
├── startup.sh
├── config/            # settings, urls, wsgi
└── tienda/            # app: modelos, admin, dashboard
```

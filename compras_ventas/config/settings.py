"""
Configuración de Django para el proyecto compras_ventas.
Preparada para desplegar en Azure App Service (Linux, Python).
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Seguridad ---------------------------------------------------------------
# En local usa un valor por defecto; en Azure define SECRET_KEY en la config.
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "dev-inseguro-cambiar-en-produccion-1234567890"
)

# DEBUG=False por defecto. En local exporta DEBUG=1 si lo necesitas.
DEBUG = os.environ.get("DEBUG", "0") == "1"

# Azure App Service inyecta WEBSITE_HOSTNAME con el dominio del sitio.
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
_azure_host = os.environ.get("WEBSITE_HOSTNAME")
if _azure_host:
    ALLOWED_HOSTS.append(_azure_host)
    CSRF_TRUSTED_ORIGINS = [f"https://{_azure_host}"]

# Permite añadir hosts extra por variable de entorno (separados por coma).
_extra_hosts = os.environ.get("ALLOWED_HOSTS", "")
if _extra_hosts:
    ALLOWED_HOSTS += [h.strip() for h in _extra_hosts.split(",") if h.strip()]

# --- Aplicaciones ------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "tienda",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise sirve los estáticos sin necesidad de un servidor extra.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- Base de datos -----------------------------------------------------------
# Por defecto SQLite (lo más ligero). En Azure el disco es efímero: los datos
# se pierden al reiniciar/redeployar. Para persistencia real define DATABASE_URL
# apuntando a Azure Database for PostgreSQL (ver README).
_database_url = os.environ.get("DATABASE_URL")
if _database_url:
    # Parser mínimo de postgres://user:pass@host:port/dbname
    from urllib.parse import urlparse

    _u = urlparse(_database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": _u.path.lstrip("/"),
            "USER": _u.username,
            "PASSWORD": _u.password,
            "HOST": _u.hostname,
            "PORT": _u.port or 5432,
            "OPTIONS": {"sslmode": "require"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internacionalización ----------------------------------------------------
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Mexico_City"
USE_I18N = True
USE_TZ = True

# --- Archivos estáticos (servidos por WhiteNoise) ----------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Tras el login, redirige al panel.
LOGIN_REDIRECT_URL = "/"
LOGIN_URL = "/admin/login/"

# Ajustes de seguridad recomendados en producción.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

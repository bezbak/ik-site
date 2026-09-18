"""
Django settings for the AVAT 365 site (config project).
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Loads a .env file from the project root if one exists (no-op otherwise, so
# this never affects a host that sets real environment variables directly).
load_dotenv(BASE_DIR / ".env")

# SECURITY WARNING: keep the secret key used in production secret!
# Set DJANGO_SECRET_KEY in the environment for real deployments.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-dev-only-key-change-me-in-production",
)

# Set DJANGO_DEBUG=0 in production.
DEBUG = os.environ.get("DJANGO_DEBUG", "1") == "1"

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()
]
if DEBUG:
    ALLOWED_HOSTS += ["localhost", "127.0.0.1"]
if not ALLOWED_HOSTS:
    # Safe fallback so a first deploy doesn't 400 before ALLOWED_HOSTS is configured.
    ALLOWED_HOSTS = ["*"]

# Railway (and most PaaS) terminate TLS at a proxy and forward plain HTTP,
# setting X-Forwarded-Proto to say so. Without this, request.is_secure() is
# always False, so Django's CSRF Origin check compares "http://" against the
# browser's "https://" Origin header and every POST (admin login included)
# gets rejected with a CSRF 403.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CSRF_TRUSTED_ORIGINS needs a scheme (ALLOWED_HOSTS doesn't), so derive it
# from the same host list instead of keeping a second list in sync.
CSRF_TRUSTED_ORIGINS = [
    f"https://{host}" for host in ALLOWED_HOSTS if host not in ("localhost", "127.0.0.1")
]


INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    "jazzmin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
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
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "catalog.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database.
# SQLite by default (fine for a low-traffic brochure site with an admin panel).
# On a host with an ephemeral filesystem (e.g. Railway), set DJANGO_DB_PATH to a
# path on a mounted persistent volume so the database survives redeploys.
# For Postgres, set DATABASE_URL and add dj-database-url later.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", str(BASE_DIR / "db.sqlite3")),
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True


# Static files: the exported site's own img/, assets/, video/, documents/ folders
# live under public/ and are served at the site root by WhiteNoise (WHITENOISE_ROOT),
# so every existing "img/x.jpg"-style relative reference keeps working unchanged.
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
WHITENOISE_ROOT = BASE_DIR / "public"
# Separate, small static dir (not `public/`) for admin-only assets like the
# Jazzmin logo/favicon, so collectstatic doesn't copy the whole exported site.
STATICFILES_DIRS = [BASE_DIR / "static"]

# Admin-uploaded media (floor plans, gallery photos, PDFs).
# Point DJANGO_MEDIA_ROOT at a mounted persistent volume in production, or
# uploads will be lost on the next deploy/restart.
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.environ.get("DJANGO_MEDIA_ROOT", str(BASE_DIR / "media")))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# A brochure site behind a simple admin panel; no need to lock down file uploads
# further than Django's own validation for this use case.
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024


# django-jazzmin: admin theme. Branded for AVAT 365 (navy/blue from the site's
# own palette) so the admin doesn't look like bare stock Django.
JAZZMIN_SETTINGS = {
    "site_title": "AVAT 365 — админка",
    "site_header": "AVAT 365",
    "site_brand": "AVAT 365",
    "site_logo": "img/logo-blue.png",
    "login_logo": "img/logo-blue.png",
    "site_icon": "img/favicon.png",
    "site_logo_classes": "img-square",
    "welcome_sign": "Панель управления сайтом AVAT 365",
    "copyright": "AVAT 365",
    "search_model": ["catalog.Property", "catalog.Document"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": "Смотреть сайт", "url": "/", "new_window": True},
        {"model": "catalog.Property"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "catalog",
        "catalog.Property",
        "catalog.PropertyImage",
        "catalog.Document",
        "catalog.FAQItem",
        "catalog.SiteSettings",
        "auth",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "catalog.Property": "fas fa-home",
        "catalog.PropertyImage": "fas fa-images",
        "catalog.Document": "fas fa-file-pdf",
        "catalog.FAQItem": "fas fa-circle-question",
        "catalog.SiteSettings": "fas fa-gear",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "catalog.Property": "collapsible",
    },
    "language_chooser": False,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "flatly",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}

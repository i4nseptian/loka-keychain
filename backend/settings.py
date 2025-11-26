"""
Django settings for backend project.
Optimized for Vercel deployment - FIXED VERSION
"""

from pathlib import Path
import os
import dj_database_url

# ----------------------------
# 🔧 PATH & BASIC CONFIG
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-uas^c%rmqdl^vi46vssw7%(z^vnel2af(@rh-5sxs0-2b17$(y')

# ✅ Production: DEBUG akan False di Vercel
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ✅ Allow Vercel domains
ALLOWED_HOSTS = [
    '.vercel.app',
    '.now.sh',
    'localhost',
    '127.0.0.1',
]

# ----------------------------
# ⚙️ APPS
# ----------------------------
INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "products",
]

# ----------------------------
# 🧠 MIDDLEWARE
# ----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = "backend.urls"

# ----------------------------
# 🧩 TEMPLATE ENGINE
# ----------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# ----------------------------
# 🗄 DATABASE
# ----------------------------
if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    # Development only - SQLite lokal
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# ----------------------------
# 🔐 PASSWORD VALIDATION
# ----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ----------------------------
# 🌍 I18N
# ----------------------------
LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Makassar"
USE_I18N = True
USE_TZ = True

# ----------------------------
# 📦 STATIC FILES (CSS, JS, Images)
# ----------------------------
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# ✅ Django 4.2+ STORAGES (ganti STATICFILES_STORAGE yang deprecated)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ----------------------------
# 🖼️ MEDIA FILES (Upload gambar produk)
# ----------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------
# 🌐 CORS - Vercel production
# ----------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = True

# ----------------------------
# 🧠 UNFOLD ADMIN CONFIG
# ----------------------------
UNFOLD = {
    "SITE_TITLE": "LOKA.CO Admin",
    "SITE_HEADER": "LOKA.CO Dashboard",
    "SITE_URL": "/",
    "SITE_LOGO": {
        "src": "/static/img/logo loka.png",
        "alt": "LOKA.CO",
        "width": "150",
        "height": "50",
    },
    "FAVICON": "/static/img/logo loka.png",
    "THEME": "dark",
    "COLORS": {
        "primary": {
            "500": "#1c1c75",
            "600": "#15155a",
            "700": "#101046",
        },
        "accent": {
            "500": "#00bcd4",
        },
        "neutral": {
            "100": "#f3f3f7",
            "900": "#0a0a23",
        },
    },
    "FONTS": {
        "heading": "Poppins, sans-serif",
        "body": "Inter, sans-serif",
    },
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "STYLES": ["/static/css/costum_admin.css"],
    "SCRIPTS": [],
}

# ============================================
# 💳 MIDTRANS PAYMENT PRODUCTION
# ============================================
MIDTRANS_IS_PRODUCTION = True
MIDTRANS_SERVER_KEY = os.environ.get('MIDTRANS_SERVER_KEY', "Mid-server-es3mcyeUd2ERi-dszey7_bnX")
MIDTRANS_CLIENT_KEY = os.environ.get('MIDTRANS_CLIENT_KEY', "Mid-client-B3310bjceOS1GUiv")
MIDTRANS_MERCHANT_ID = os.environ.get('MIDTRANS_MERCHANT_ID', "G655962966")

# ============================================
# 🔒 CSRF SETTINGS - Vercel Production
# ============================================
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'https://*.vercel.app',
]

# Session settings
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ============================================
# 🚀 VERCEL PRODUCTION SETTINGS
# ============================================
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
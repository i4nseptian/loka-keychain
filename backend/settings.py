"""
Django settings for backend project.
"""

from pathlib import Path
import os

# ----------------------------
# 🔧 PATH & BASIC CONFIG
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-uas^c%rmqdl^vi46vssw7%(z^vnel2af(@rh-5sxs0-2b17$(y')

# ✅ Production-ready: False di production
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ✅ Railway akan auto-inject domain
ALLOWED_HOSTS = ['*']

# ----------------------------
# ⚙️ APPS
# ----------------------------
INSTALLED_APPS = [
    "unfold",  # 🧩 UI Admin Modern
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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Railway static files
    'corsheaders.middleware.CorsMiddleware',  # ✅ CORS harus di atas
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

# ✅ Railway: collectstatic output
STATIC_ROOT = BASE_DIR / "staticfiles"

# ✅ WhiteNoise: compress & cache static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# ----------------------------
# 🖼️ MEDIA FILES (Upload gambar produk)
# ----------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ----------------------------
# 🌐 CORS - Railway production
# ----------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# ✅ Allow Railway domain (auto-added saat deploy)
CORS_ALLOW_ALL_ORIGINS = False  # Set True kalau mau allow semua origin

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
# 🔐 CSRF SETTINGS - Railway Production
# ============================================
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'

# ✅ Tambahkan Railway domain nanti setelah deploy
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:9000',
    'http://localhost:9000',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    # Railway domain akan ditambahkan nanti: 'https://loka-keychain-production.up.railway.app'
]

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_SAVE_EVERY_REQUEST = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# ============================================
# 🚀 RAILWAY PRODUCTION SETTINGS
# ============================================
# Security settings untuk production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_CONTENT_TYPE_NOSNIFF = True
import os
from pathlib import Path
import dj_database_url
import environ

# Cloudinary imports
import cloudinary
import cloudinary.api
import cloudinary.uploader

BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================================
# ENVIRONMENT VARIABLES
# ==========================================================
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

# ==========================================================
# HOSTS & SECURITY CONFIGURATION
# ==========================================================
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'dinas-catering-rentals-services-backend.onrender.com', # Your backend host URL
    '.onrender.com',                                         # Catch-all wildcard for Render subdomains
]

# ==========================================================
# CORS CONFIGURATION
# ==========================================================
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.43.200:3000",
    "https://dinacatering.com",
    "https://www.dinacatering.com",
    "https://dinas-catering-rentals-services-fro.vercel.app", # Added your exact Vercel staging domain here
]

FRONTEND_URL = env("FRONTEND_URL", default=None)
if FRONTEND_URL and FRONTEND_URL not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_URL)

# ==========================================================
# CSRF TRUSTED ORIGINS (Moved completely out of the if-block)
# ==========================================================

CSRF_TRUSTED_ORIGINS = [
    "https://dinacatering.com",
    "https://www.dinacatering.com",
    "https://dinas-catering-rentals-services-fro.vercel.app",
    "https://dinas-catering-rentals-services-backend.onrender.com"
]

# ==========================================================
# APPLICATIONS
# ==========================================================
INSTALLED_APPS = [
    "django.contrib.staticfiles",  
    "cloudinary_storage",          
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # Third-party
    "rest_framework",
    "corsheaders",
    "cloudinary",
    # Local apps
    "services",
]

# ==========================================================
# MIDDLEWARE
# ==========================================================
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Placed perfectly below security middleware
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# ==========================================================
# TEMPLATES
# ==========================================================
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

WSGI_APPLICATION = "core.wsgi.application"

# ==========================================================
# DATABASE
# ==========================================================
DATABASES = {
    "default": dj_database_url.config(
        default=env("DATABASE_URL"),
        conn_max_age=600,  
        ssl_require=True   
    )
}

#DATABASES = {"default": dj_database_url.config(default=env("DATABASE_URL"))}


# ==========================================================
# CLOUDINARY CONFIGURATION
# ==========================================================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": env("CLOUDINARY_API_KEY"),
    "API_SECRET": env("CLOUDINARY_API_SECRET"),
}

# ==========================================================
# STORAGES (Django 6.0+ Unified Standard - Cleaned & De-duplicated)
# ==========================================================
STORAGES = {
    # Media goes to Cloudinary
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    # Force WhiteNoise to use standard file storage backend (safest from FileNotFoundError checks)
    "staticfiles": {
        "BACKEND": "whitenoise.storage.StaticFilesStorage",
    },
}

# The legacy compatibility bypass for django-cloudinary-storage
STATICFILES_STORAGE = "whitenoise.storage.StaticFilesStorage"

# ==========================================================
# EMAIL CONFIGURATION (Brevo)
# ==========================================================
BREVO_API_KEY = env("BREVO_API_KEY")
BREVO_SENDER_EMAIL = env("BREVO_SENDER_EMAIL")
BREVO_SENDER_NAME = env("BREVO_SENDER_NAME")
DEFAULT_FROM_EMAIL = env("BREVO_SENDER_EMAIL")

# ==========================================================
# INTERNATIONALIZATION & AUTH
# ==========================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==========================================================
# STATIC & MEDIA URLS / PATHS
# ==========================================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ==========================================================
# PRODUCTION SECURITY
# ==========================================================
if not DEBUG:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# ==========================================================
# PAYSTACK PAYMENT GATEWAY CONFIGURATION
# ==========================================================
PAYSTACK_SECRET_KEY = env("PAYSTACK_SECRET_KEY")
PAYSTACK_VERIFY_URL = env("PAYSTACK_VERIFY_URL", default="https://api.paystack.co/transaction/verify/")
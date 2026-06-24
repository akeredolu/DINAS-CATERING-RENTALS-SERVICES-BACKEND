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

# ==========================================================
# CORE SETTINGS
# ==========================================================
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "dinacatering.com",
    "www.dinacatering.com",
    "api.dinacatering.com",
    "dinas-catering-rentals-services-backend.onrender.com",  
]

# ==========================================================
# APPLICATIONS
# ==========================================================
INSTALLED_APPS = [
    "cloudinary_storage",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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
DATABASES = {"default": dj_database_url.config(default=env("DATABASE_URL"))}

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
]

# ==========================================================
# CLOUDINARY CONFIGURATION
# ==========================================================
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": env("CLOUDINARY_API_KEY"),
    "API_SECRET": env("CLOUDINARY_API_SECRET"),
}

# ==========================================================
# STORAGES (Django 6.0+ Unified Standard)
# ==========================================================
STORAGES = {
    # Media goes to Cloudinary
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    # Static files go through WhiteNoise for production speed and reliability
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

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
#STATICFILES_DIRS = [BASE_DIR / "static"]

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
# STORAGES (Django 6.0+ Unified Standard)
# ==========================================================
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# Add this line below to trick django-cloudinary-storage and stop the crash:
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
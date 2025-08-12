import os.path
from pathlib import Path

from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")


INTERNAL_IPS = [
    "127.0.0.1",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    # Project Apps
    "apps.campus",
    "apps.accounts",
    "apps.threads",
    "apps.posts",
    "apps.comments",
    "apps.votes",
    # Third Party Apps
    "django_tailwind_cli",
    "widget_tweaks",
    "django_htmx",
    "template_partials",
    "django_cotton",
    "lucide",
    # Django Allauth
    "allauth",
    "allauth.account",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # allauth
    "django_htmx.middleware.HtmxMiddleware",  # htmx
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": False,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "builtins": [
                "lucide.templatetags.lucide",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_URL = "static/"

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = "/media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

SITE_ID = 1
AUTH_USER_MODEL = "accounts.User"

# Allauth configuration
ACCOUNT_LOGIN_METHODS = {"username", "email"}
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USER_MODEL_USERNAME_FIELD = "username"
ACCOUNT_USER_MODEL_EMAIL_FIELD = "email"
ACCOUNT_SIGNUP_FIELDS = [
    "first_name*",
    "last_name*",
    "email*",
    "username*",
    "password1*",
    "password2*",
]

ACCOUNT_FORMS = {
    "signup": "apps.accounts.forms.CustomSignupForm",
}

ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/m",  # 5 attempts per minute
}

ACCOUNT_SIGNUP_REDIRECT_URL = "/accounts/login/"
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

TAILWIND_CLI_SRC_CSS = "static/css/source.css"
TAILWIND_CLI_DIST_CSS = "css/dist/tailwind.min.css"
TAILWIND_CLI_AUTOMATIC_DOWNLOAD = False
TAILWIND_CLI_USE_DAISY_UI = True
TAILWIND_CLI_PATH = "/usr/local/bin/tailwindcss"

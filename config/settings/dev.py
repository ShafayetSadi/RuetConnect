from config.settings.base import *  # noqa F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS += [  # noqa F405
    "django_browser_reload",
    # "django_extensions",
]

MIDDLEWARE += [  # noqa F405
    "django_browser_reload.middleware.BrowserReloadMiddleware",  # django-browser-reload
]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

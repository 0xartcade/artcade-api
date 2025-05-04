import re

import dj_database_url

from .common import *

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    "default": (
        dj_database_url.config(env="DATABASE_URL")
        | {
            "ATOMIC_REQUESTS": True,
        }
    ),
}

# Override log level
LOGGING["root"]["level"] = logging.WARNING  # noqa
LOGGING["loggers"]["django_structlog"]["level"] = logging.WARNING  # noqa

# CORS
CORS_ALLOWED_ORIGINS = []
CORS_ALLOWED_ORIGIN_REGEXES = [
    # artade projects - match subdomains + root domain
    re.compile(r"^https://([\w-]+\.)?0xartcade\.xyz$"),
]

# CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://*.0xartcade.xyz",
]

# Allow django to detect if request was made via https.
# this header is set by the Elastic Load Balancer
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Hardcoded settings
APP_CHAIN_ID = 360

# Know Your Memes
KYM_GAME_ADDRESS = "0x6bD4A37Fc5753425fA566103a51Fd7355d940D48"
KYM_GAME_DURATION = timedelta(seconds=30)  # noqa
KYM_MAX_QUESTIONS = 5

# AUTH
AUTH_COOKIE_NAME = "artcade_auth_cookie"

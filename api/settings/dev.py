# import re

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
CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS = []
# CORS_ALLOWED_ORIGIN_REGEXES = [
#     # artade projects - match subdomains + root domain
#     re.compile(r"^https://([\w-]+\.)?0xartcade\.xyz$"),
#     # Allow localhost with any port.
#     re.compile(r"^http://localhost:\d+$"),
#     # Allow vercel preview links but only for our app.
#     re.compile(r"^https://([\w-]+)-artcade.vercel\.app$"),
# ]

# CSRF
CSRF_TRUSTED_ORIGINS = [
    "https://*.0xartcade.xyz",
    "https://*.vercel.app",
    *[f"http://localhost:{port}" for port in range(3000, 3010)],
    *[f"http://localhost.local:{port}" for port in range(3000, 3010)],
]

# Allow django to detect if request was made via https.
# this header is set by the Elastic Load Balancer
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

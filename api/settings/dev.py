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

# CORS
CORS_ALLOWED_ORIGINS = []
CORS_ALLOWED_ORIGIN_REGEXES = [
    # Allow localhost with any port.
    re.compile(r"^http://localhost:\d+$"),
    # Allow vercel preview links but only for our app.
    re.compile(r"^https://([\w-]+)-artcade.vercel\.app$"),
]

# Allow django to detect if request was made via https.
# this header is set by the Elastic Load Balancer
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

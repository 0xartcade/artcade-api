"""
At import, it fetches all the questions from the secret endpoint and stores
in memory as variables that can be accessed on demand without dealing with egress/ingress issues.
"""

import httpx
from django.conf import settings


def get_data():
    response = httpx.get(settings.KYM_QUESTION_DATA_URL)
    data = response.json()

    return data


_data = get_data()
QUESTIONS = _data["questions"]
TITLES = _data["titles"]
ARTISTS = _data["artists"]
SUPPLIES = _data["supplies"]
SEASONS = _data["seasons"]

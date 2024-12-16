import hmac
import json

import pytest
from django.contrib.auth import get_user_model

from games.models import PlayerHighScore
from tests.factories import GameFactory
from webhooks.models import Webhook

pytestmark = [pytest.mark.django_db(transaction=True)]

User = get_user_model()


def test_invalid_signature(api_client):
    Webhook.objects.create(
        webhook_id="wh_6l5v7cnr8qidv5fe",
        signing_key="test-signing-key",
    )

    with open("tests/webhooks/register.json", "r") as f:
        data = json.load(f)

    signature = (
        hmac.HMAC(
            key=bytes("bad signing key", "utf-8"),
            msg=json.dumps(data).replace(" ", "").encode("utf-8"),
            digestmod="sha256",
        )
        .digest()
        .hex()
    )

    response = api_client.post(
        "/games/index/player-high-score",
        data,
        headers={"x-alchemy-signature": signature},
    )

    assert response.status_code == 400

    # try sending without a header
    response = api_client.post(
        "/games/index/player-high-score",
        data,
    )

    assert response.status_code == 400


def test_webhook_not_found(api_client):
    webhook = Webhook.objects.create(
        webhook_id="test-webhook",
        signing_key="test-signing-key",
    )

    with open("tests/webhooks/register.json", "r") as f:
        data = json.load(f)

    signature = (
        hmac.HMAC(
            key=bytes(webhook.signing_key, "utf-8"),
            msg=json.dumps(data).replace(" ", "").encode("utf-8"),
            digestmod="sha256",
        )
        .digest()
        .hex()
    )

    response = api_client.post(
        "/games/index/player-high-score",
        data,
        headers={"x-alchemy-signature": signature},
    )

    assert response.status_code == 404


def test_index_player_registered(api_client):
    user = User.objects.create(eth_address="0x181f59eb6490c8bf73d291af0d5a56dc90d7cd8b")
    game = GameFactory(eth_address="0x6bd4a37fc5753425fa566103a51fd7355d940d48")

    webhook = Webhook.objects.create(
        webhook_id="wh_6l5v7cnr8qidv5fe",
        signing_key="test-signing-key",
    )

    with open("tests/webhooks/register.json", "r") as f:
        data = json.load(f)

    signature = (
        hmac.HMAC(
            key=bytes(webhook.signing_key, "utf-8"),
            msg=json.dumps(data).replace(" ", "").encode("utf-8"),
            digestmod="sha256",
        )
        .digest()
        .hex()
    )

    response = api_client.post(
        "/games/index/player-high-score",
        data,
        headers={"x-alchemy-signature": signature},
    )

    assert response.status_code == 200

    phs = PlayerHighScore.objects.get(
        user=user,
        game=game,
    )

    assert phs.score == 0


def test_index_player_registered_and_high_score(api_client):
    user = User.objects.create(eth_address="0x181f59eb6490c8bf73d291af0d5a56dc90d7cd8b")
    game = GameFactory(eth_address="0x6bd4a37fc5753425fa566103a51fd7355d940d48")

    webhook = Webhook.objects.create(
        webhook_id="wh_6l5v7cnr8qidv5fe",
        signing_key="test-signing-key",
    )

    with open("tests/webhooks/register-and-high-score.json", "r") as f:
        data = json.load(f)

    signature = (
        hmac.HMAC(
            key=bytes(webhook.signing_key, "utf-8"),
            msg=json.dumps(data).replace(" ", "").encode("utf-8"),
            digestmod="sha256",
        )
        .digest()
        .hex()
    )

    response = api_client.post(
        "/games/index/player-high-score",
        data,
        headers={"x-alchemy-signature": signature},
    )

    assert response.status_code == 200

    phs = PlayerHighScore.objects.get(
        user=user,
        game=game,
    )

    assert phs.score == 1000


def test_index_player_high_score(api_client):
    user = User.objects.create(eth_address="0xf4db918906946b53c8db2292239ac1c8b94145f6")
    game = GameFactory(eth_address="0x6bd4a37fc5753425fa566103a51fd7355d940d48")

    webhook = Webhook.objects.create(
        webhook_id="wh_6l5v7cnr8qidv5fe",
        signing_key="test-signing-key",
    )

    with open("tests/webhooks/high-score.json", "r") as f:
        data = json.load(f)

    signature = (
        hmac.HMAC(
            key=bytes(webhook.signing_key, "utf-8"),
            msg=json.dumps(data).replace(" ", "").encode("utf-8"),
            digestmod="sha256",
        )
        .digest()
        .hex()
    )

    response = api_client.post(
        "/games/index/player-high-score",
        data,
        headers={"x-alchemy-signature": signature},
    )

    assert response.status_code == 200

    phs = PlayerHighScore.objects.get(
        user=user,
        game=game,
    )

    assert phs.score == 3300

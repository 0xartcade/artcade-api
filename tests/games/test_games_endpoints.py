from hashlib import sha256

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from hexbytes import HexBytes

from games.models import PlayerScore
from tests.factories import GameFactory, PlayerHighScoreFactory, PlayerScoreFactory

pytestmark = [pytest.mark.django_db(transaction=True)]

User = get_user_model()


def test_get_game(api_client):
    game = GameFactory()
    response = api_client.get(f"/games/{game.id}")
    assert (
        response.status_code == 200
        and response.data["id"] == game.id
        and response.data["name"] == game.name
        and response.data["description"] == game.description
        and response.data["eth_address"] == game.eth_address
        and response.data["url"] == game.url
        and response.data["nft_address"] == game.nft_address
    )


@pytest.mark.parametrize("num", [1, 10, 100])
def test_get_games(num: int, api_client):
    games = GameFactory.create_batch(num)

    response = api_client.get("/games")
    assert (
        response.status_code == 200
        and response.data["count"] == num
        and all(
            [
                data["id"] == game.id
                and data["name"] == game.name
                and data["description"] == game.description
                and data["eth_address"] == game.eth_address
                and data["url"] == game.url
                and data["nft_address"] == game.nft_address
                for data, game in zip(response.data["results"], games)
            ]
        )
    )


@pytest.mark.parametrize("num", [1, 10, 100])
def test_get_leaderboard(num, api_client):
    game = GameFactory()
    high_scores = PlayerHighScoreFactory.create_batch(num, game=game)
    sorted_high_scores = sorted(high_scores, key=lambda x: x.score, reverse=True)

    response = api_client.get(f"/leaderboard/{game.id}")

    assert (
        response.status_code == 200
        and response.data["count"] == num
        and all(
            [
                data["username"] == high_score.user.username
                and data["eth_address"] == high_score.user.eth_address
                and data["score"] == high_score.score
                and data["token_id"] == high_score.token_id
                for data, high_score in zip(
                    response.data["results"], sorted_high_scores
                )
            ]
        )
    )


@pytest.mark.parametrize("num", [1, 10, 100])
def test_get_player_high_scores(num, auth_client):
    user = User.objects.get(eth_address__iexact=auth_client.eth_address)
    games = GameFactory.create_batch(num)

    high_scores = []
    for game in games:
        high_scores.append(PlayerHighScoreFactory(user=user, game=game))

    # add random high scores from other users
    PlayerHighScoreFactory.create_batch(num)

    response = auth_client.get("/high-scores")

    assert (
        response.status_code == 200
        and response.data["count"] == num
        and all(
            [
                data["game"]["id"] == high_score.game.id
                and data["score"] == high_score.score
                and data["token_id"] == high_score.token_id
                for data, high_score in zip(response.data["results"], high_scores)
            ]
        )
    )


def test_get_player_high_score_for_game(auth_client):
    user = User.objects.get(eth_address__iexact=auth_client.eth_address)
    phs = PlayerHighScoreFactory(user=user)

    response = auth_client.get(f"/high-scores/{phs.game.id}")

    assert (
        response.status_code == 200
        and response.data["game"]["id"] == phs.game.id
        and response.data["score"] == phs.score
        and response.data["token_id"] == phs.token_id
    )


@pytest.mark.parametrize("num", [1, 10, 100])
def test_get_player_scores(num: int, auth_client):
    user = User.objects.get(eth_address__iexact=auth_client.eth_address)
    player_scores = PlayerScoreFactory.create_batch(num, user=user)

    response = auth_client.get("/scores")

    assert (
        response.status_code == 200
        and response.data["count"] == num
        and all(
            [
                data["game"]["id"] == player_score.game.id
                and data["score"] == player_score.score
                for data, player_score in zip(response.data["results"], player_scores)
            ]
        )
    )


@pytest.mark.parametrize(
    "num",
    [1, 10, 100],
)
def test_get_signed_scores(num, auth_client):
    user = User.objects.get(eth_address__iexact=auth_client.eth_address)
    player_scores = PlayerScoreFactory.create_batch(num, user=user)

    response = auth_client.post(
        "/scores/sign", data={"ids": [score.id for score in player_scores]}
    )

    assert response.status_code == 200 and all(
        [
            data["player"] == user.eth_address
            and data["score"] == score.score
            and data["game_address"] == score.game.eth_address
            and data["nonce"] == f"0x{sha256(HexBytes(score.id)).hexdigest()}"
            and len(data["signature"]) == 65 * 2 + 2
            for data, score in zip(response.data, player_scores)
        ]
    )


@pytest.mark.parametrize(
    "num",
    [1, 10, 100],
)
def test_delete_signed_scores(num, auth_client):
    user = User.objects.get(eth_address__iexact=auth_client.eth_address)
    player_scores = PlayerScoreFactory.create_batch(num, user=user)

    assert PlayerScore.objects.filter(user=user).count() == num

    response = auth_client.delete(
        "/scores/delete", data={"ids": [score.id for score in player_scores]}
    )

    assert (
        response.status_code == 200
        and PlayerScore.objects.filter(user=user).count() == 0
    )


def test_get_ticket_metadata(api_client):
    response = api_client.get("/ticket/metadata")
    assert (
        response.status_code == 200
        and response.data["name"] == settings.TICKET_NAME
        and response.data["description"] == settings.TICKET_DESCRIPTION
        and response.data["image"] == settings.TICKET_IMAGE_URL
    )

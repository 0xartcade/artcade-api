from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from freezegun import freeze_time

from know_your_memes.models import Gameplay, Question

pytestmark = [pytest.mark.django_db(transaction=True)]

User = get_user_model()


@pytest.mark.parametrize(
    ["time_to_wait", "expected_score"], [[0, 6000], [10, 4000], [20, 2000], [30, 0]]
)
def test_calculate_score(time_to_wait, expected_score, auth_client):
    user = User.objects.get(eth_address__iexact=auth_client.eth_address)
    gameplay = Gameplay.objects.create(user=user)
    question = Question.objects.create(
        gameplay=gameplay,
        token_id=1,
        image_url="https://google.com",
        blurhash="asldkjlags",
        color="#545454",
        title="one",
        artist="two",
        supply=10,
        season=1,
        title_options=[],
        artist_options=[],
        supply_options=[],
        season_options=[],
    )

    # answer
    with freeze_time(now() + timedelta(seconds=time_to_wait)):
        question.title_answer = "one"
        question.artist_answer = "two"
        question.supply_answer = 10
        question.season_answer = 1
        question.save()

    # calculate score
    score = question.calculate_score()
    question.refresh_from_db()

    assert abs(expected_score - score) < 5  # variance
    assert score == question.score

    # calculate score again, asserting it stays the same
    score = question.calculate_score()
    question.refresh_from_db()

    assert abs(expected_score - score) < 5  # variance
    assert score == question.score


def test_calculate_score_did_not_answer(auth_client):
    user = User.objects.get(eth_address__iexact=auth_client.eth_address)
    gameplay = Gameplay.objects.create(user=user)
    question = Question.objects.create(
        gameplay=gameplay,
        token_id=1,
        image_url="https://google.com",
        blurhash="asldkjlags",
        color="#545454",
        title="one",
        artist="two",
        supply=10,
        season=1,
        title_options=[],
        artist_options=[],
        supply_options=[],
        season_options=[],
    )

    score = question.calculate_score()
    question.refresh_from_db()

    assert score == 0
    assert score == question.score

    # run again
    score = question.calculate_score()
    question.refresh_from_db()

    assert score == 0
    assert score == question.score

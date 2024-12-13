from datetime import timedelta

import pytest
from django.conf import settings
from django.utils.timezone import now
from freezegun import freeze_time

from know_your_memes.models import Gameplay, Question
from know_your_memes.questions import QUESTIONS
from tests.factories import GameFactory

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_create_gameplay(auth_client):
    response = auth_client.post("/kym/gameplay")

    gameplay = Gameplay.objects.first()

    assert (
        response.status_code == 200
        and len(Gameplay.objects.all()) == 1
        and response.data["id"] == gameplay.id
        and gameplay.user.eth_address == auth_client.eth_address
    )


def test_create_question(auth_client):
    auth_client.post("/kym/gameplay")
    gameplay = Gameplay.objects.first()

    response = auth_client.post(f"/kym/gameplay/{gameplay.id}/question")

    question = Question.objects.first()

    assert (
        response.status_code == 200
        and question.gameplay.id == gameplay.id
        and question.score is None
        and len(response.data["title_options"]) == 4
        and len(response.data["artist_options"]) == 4
        and len(response.data["supply_options"]) == 4
        and len(response.data["season_options"]) == 4
    )


def test_create_question_404(auth_client):
    response = auth_client.post("/kym/gameplay/69/question")

    assert response.status_code == 404


@pytest.mark.parametrize(
    ["wait_time", "expected_score"], [(0, 6000), (10, 4000), (20, 2000), (30, 0)]
)
def test_submit_question(wait_time, expected_score, auth_client):
    auth_client.post("/kym/gameplay")
    gameplay = Gameplay.objects.first()

    # create question
    r1 = auth_client.post(f"/kym/gameplay/{gameplay.id}/question")

    # find answer
    answer = QUESTIONS[r1.data["token_id"] - 1]

    # submit wait seconds later
    with freeze_time(now() + timedelta(seconds=wait_time)):
        r2 = auth_client.post(
            f"/kym/question/{r1.data['id']}/submit",
            data={
                "title": answer["questions"]["title"],
                "artist": answer["questions"]["artist"],
                "supply": answer["questions"]["supply"],
                "season": answer["questions"]["season"],
            },
        )

    # verify
    assert (
        r2.status_code == 200
        and abs(r2.data["score"] - expected_score) < 5
        and r2.data["title"] == r2.data["title_answer"]
        and r2.data["artist"] == r2.data["artist_answer"]
        and r2.data["supply"] == r2.data["supply_answer"]
        and r2.data["season"] == r2.data["season_answer"]
    )


def test_submit_question_404(auth_client):
    r = auth_client.post("/kym/gameplay/420/question")

    assert r.status_code == 404


@pytest.mark.parametrize(
    ["wait_time", "expected_score"], [(0, 30_000), (10, 20_000), (20, 10_000), (30, 0)]
)
def test_submit_gameplay(wait_time, expected_score, auth_client):
    # create game
    GameFactory(eth_address=settings.KYM_GAME_ADDRESS)
    r = auth_client.post("/kym/gameplay")
    gameplay = Gameplay.objects.first()

    for _ in range(settings.KYM_MAX_QUESTIONS):
        # create question
        r1 = auth_client.post(f"/kym/gameplay/{gameplay.id}/question")

        # find answer
        answer = QUESTIONS[r1.data["token_id"] - 1]

        # submit wait seconds later
        with freeze_time(now() + timedelta(seconds=wait_time)):
            auth_client.post(
                f"/kym/question/{r1.data['id']}/submit",
                data={
                    "title": answer["questions"]["title"],
                    "artist": answer["questions"]["artist"],
                    "supply": answer["questions"]["supply"],
                    "season": answer["questions"]["season"],
                },
            )

    # done answering questions
    r = auth_client.post(f"/kym/gameplay/{gameplay.id}/submit")

    assert (
        r.status_code == 200
        and abs(r.data["total_score"] - expected_score) < 10
        and len(r.data["questions"]) == 5
    )

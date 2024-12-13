import pytest
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from games.models import Game, PlayerHighScore, PlayerScore

User = get_user_model()

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_unique_user_game():
    game = Game.objects.create(name="Test Game", eth_address="0x1234")
    user = User.objects.create(username="testuser")
    PlayerHighScore.objects.create(user=user, game=game, score=100, token_id=1)

    with pytest.raises(IntegrityError):
        PlayerHighScore.objects.create(user=user, game=game, score=1000, token_id=10)


def test_not_unique_score():
    game = Game.objects.create(name="Test Game", eth_address="0x1234")
    user = User.objects.create(username="testuser")
    PlayerScore.objects.create(user=user, game=game, score=1)
    PlayerScore.objects.create(user=user, game=game, score=10)
    PlayerScore.objects.create(user=user, game=game, score=100)

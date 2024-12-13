from secrets import token_hex

from django.contrib.auth import get_user_model
from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from games.models import Game, PlayerHighScore, PlayerScore

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("user_name")
    eth_address = LazyAttribute(lambda _: f"0x{token_hex(20)}")


class GameFactory(DjangoModelFactory):
    class Meta:
        model = Game

    name = Faker("company")
    description = Faker("paragraph")
    eth_address = LazyAttribute(lambda _: f"0x{token_hex(20)}")
    url = Faker("url")
    nft_address = LazyAttribute(lambda _: f"0x{token_hex(20)}")
    signing_key = LazyAttribute(lambda _: f"0x{token_hex(32)}")


class PlayerHighScoreFactory(DjangoModelFactory):
    class Meta:
        model = PlayerHighScore

    user = SubFactory(UserFactory)
    game = SubFactory(GameFactory)
    score = Faker("pyint")
    token_id = Faker("pyint")


class PlayerScoreFactory(DjangoModelFactory):
    class Meta:
        model = PlayerScore

    user = SubFactory(UserFactory)
    game = SubFactory(GameFactory)
    score = Faker("pyint")

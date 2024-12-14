from rest_framework.serializers import (
    CharField,
    IntegerField,
    ListField,
    ModelSerializer,
    Serializer,
)

from games.models import Game, PlayerHighScore, PlayerScore


class GameSerializer(ModelSerializer):
    class Meta:
        model = Game
        fields = [
            "id",
            "name",
            "description",
            "eth_address",
            "url",
            "nft_address",
            "created_at",
            "updated_at",
        ]


class LeaderboardSerializer(ModelSerializer):
    class Meta:
        model = PlayerHighScore
        fields = [
            "username",
            "eth_address",
            "score",
            "token_id",
            "created_at",
            "updated_at",
        ]

    username = CharField(source="user.username")
    eth_address = CharField(source="user.eth_address")


class PlayerHighScoreSerializer(ModelSerializer):
    class Meta:
        model = PlayerHighScore
        fields = [
            "game",
            "score",
            "token_id",
            "created_at",
            "updated_at",
        ]

    game = GameSerializer()


class PlayerScoreSerializer(ModelSerializer):
    class Meta:
        model = PlayerScore
        fields = [
            "id",
            "game",
            "score",
            "created_at",
            "updated_at",
        ]

    game = GameSerializer()


class SignScoreSerializer(Serializer):
    ids = ListField(child=IntegerField())


class SignedScoreSerializer(Serializer):
    player = CharField()
    score = IntegerField()
    nonce = CharField()
    signature = CharField()
    game_address = CharField()

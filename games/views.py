from hashlib import sha256

from django.contrib.auth import get_user_model
from django.http import Http404
from drf_spectacular.utils import OpenApiResponse, extend_schema
from hexbytes import HexBytes
from rest_framework.exceptions import ValidationError
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from games.helpers import sign_score
from games.models import Game, PlayerHighScore, PlayerScore
from games.serializers import (
    GameSerializer,
    LeaderboardSerializer,
    PlayerHighScoreSerializer,
    PlayerScoreSerializer,
    SignedScoreSerializer,
    SignScoreSerializer,
)

User = get_user_model()


class GameViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = GameSerializer

    def get_queryset(self):
        return Game.objects.all()


class LeaderboardViewSet(GenericViewSet, ListModelMixin):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = LeaderboardSerializer
    lookup_field = "game_id"

    def get_queryset(self):
        game_id = self.kwargs.get("game_id")
        assert game_id, "game_id is required"
        if not Game.objects.filter(id=game_id).exists():
            raise Http404("Game not found")

        return (
            PlayerHighScore.objects.filter(game_id=game_id)
            .select_related("user")
            .order_by("-score")
            .all()
        )


class PlayerHighScoreViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    serializer_class = PlayerHighScoreSerializer
    lookup_field = "game_id"

    def get_queryset(self):
        return (
            PlayerHighScore.objects.filter(user=self.request.user)
            .select_related("game")
            .order_by("game_id")
            .all()
        )


class PlayerScoreViewSet(GenericViewSet, ListModelMixin):
    serializer_class = PlayerScoreSerializer

    def get_queryset(self):
        return (
            PlayerScore.objects.filter(user=self.request.user)
            .select_related("game")
            .order_by("game_id")
            .all()
        )


class SignScoresView(APIView):
    @extend_schema(
        request=SignScoreSerializer,
        responses={200: OpenApiResponse(SignedScoreSerializer(many=True))},
    )
    def post(self, request):
        """Action to sign scores desired by the player"""

        # serialize data
        serializer = SignScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get scores
        scores = PlayerScore.objects.filter(
            user=request.user, id__in=serializer.validated_data["ids"]
        )
        if len(scores) != len(serializer.validated_data["ids"]):
            raise ValidationError(
                detail="All scores do not belong to the logged in user",
                code="invalid_scores",
            )

        # sign each score
        score_data = []
        for score in scores:
            nonce = f"0x{sha256(HexBytes(score.id)).hexdigest()}"
            score_data.append(
                {
                    "player": request.user.eth_address,
                    "score": score.score,
                    "nonce": nonce,
                    "signature": sign_score(
                        score.game.name,
                        score.game.eth_address,
                        score.game.signing_key,
                        request.user.eth_address,
                        score.score,
                        nonce,
                    ),
                    "game_address": score.game.eth_address,
                }
            )

        # return data
        ret_serializer = SignedScoreSerializer(data=score_data, many=True)
        ret_serializer.is_valid()
        return Response(data=ret_serializer.data)

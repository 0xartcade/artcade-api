from rest_framework.serializers import (
    CharField,
    IntegerField,
    ModelSerializer,
    Serializer,
)

from know_your_memes.models import Gameplay, Question


class GameplaySerializer(ModelSerializer):
    class Meta:
        model = Gameplay
        fields = ["id"]


class DemoScoreSubmissionSerializer(Serializer):
    score = IntegerField()


class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = [
            "id",
            "gameplay_id",
            "token_id",
            "image_url",
            "blurhash",
            "color",
            "title_options",
            "artist_options",
            "supply_options",
            "season_options",
        ]


class SubmitAnswerSerializer(Serializer):
    title = CharField()
    artist = CharField()
    supply = IntegerField()
    season = IntegerField()


class RevealedQuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"


class GameplayResultsSerializer(ModelSerializer):
    class Meta:
        model = Gameplay
        fields = ["id", "total_score", "questions"]

    questions = RevealedQuestionSerializer(many=True)

import random

from django.conf import settings
from django.http import Http404
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from games.models import Game, PlayerScore
from know_your_memes.models import Gameplay, Question
from know_your_memes.questions import ARTISTS, QUESTIONS, SEASONS, SUPPLIES, TITLES
from know_your_memes.serializers import (
    GameplayResultsSerializer,
    GameplaySerializer,
    QuestionSerializer,
    RevealedQuestionSerializer,
    SubmitAnswerSerializer,
)


class GameplayViewset(ViewSet):
    @extend_schema(responses={200: GameplaySerializer})
    def create_gameplay(self, request):
        """Endpoint to setup a single play of the Know Your Memes game. Questions are retrieved on-demand."""
        # get the user
        user = request.user

        # create a gameplay object
        gameplay = Gameplay.objects.create(user=user)

        # return the gameplay
        return Response(data=GameplaySerializer(gameplay).data)

    @extend_schema(responses={200: QuestionSerializer})
    def create_question(self, request, gameplay_id: int):
        """Endpoint to retrieve a new question for a gameplay"""
        # get the user
        user = request.user

        # get the gameplay
        try:
            gameplay = Gameplay.objects.prefetch_related("questions").get(
                id=gameplay_id, user=user
            )
        except Gameplay.DoesNotExist:
            raise Http404()

        # get all existing question token ids
        existing_token_ids = [
            question.token_id for question in gameplay.questions.all()
        ]

        # if all questions have been asked, return a 404
        if len(existing_token_ids) == settings.KYM_MAX_QUESTIONS:
            raise ValidationError(
                detail="All questions have been asked",
                code="all_questions_asked",
            )

        # get a random question
        random_question = random.choice(QUESTIONS)
        while random_question["token_id"] in existing_token_ids:
            random_question = random.choice(QUESTIONS)

        # create options
        title_options = [
            random_question["questions"]["title"],
            *random.choices(
                list(set(TITLES) - {random_question["questions"]["title"]}), k=3
            ),
        ]
        artist_options = [
            random_question["questions"]["artist"],
            *random.choices(
                list(set(ARTISTS) - {random_question["questions"]["artist"]}), k=3
            ),
        ]
        supply_options = [
            random_question["questions"]["supply"],
            *random.choices(
                list(set(SUPPLIES) - {random_question["questions"]["supply"]}), k=3
            ),
        ]
        season_options = [
            random_question["questions"]["season"],
            *random.choices(
                list(set(SEASONS) - {random_question["questions"]["season"]}), k=3
            ),
        ]

        # shuffle
        random.shuffle(title_options)
        random.shuffle(artist_options)
        random.shuffle(supply_options)
        random.shuffle(season_options)

        # create a question object
        question = Question.objects.create(
            gameplay=gameplay,
            image_url=random_question["image_url"],
            token_id=random_question["token_id"],
            blurhash=random_question["blurhash"],
            color=random_question["predominant_color"],
            title=random_question["questions"]["title"],
            artist=random_question["questions"]["artist"],
            supply=random_question["questions"]["supply"],
            season=random_question["questions"]["season"],
            title_options=title_options,
            artist_options=artist_options,
            supply_options=supply_options,
            season_options=season_options,
        )

        # return the question
        return Response(data=QuestionSerializer(question).data)

    @extend_schema(responses={200: GameplayResultsSerializer})
    def submit_gameplay(self, request, gameplay_id: int):
        # get the user
        user = request.user

        # get the gameplay, exiting early if the gameplay has already been submitted
        try:
            gameplay = Gameplay.objects.prefetch_related("questions").get(
                id=gameplay_id, user=user
            )
            if gameplay.total_score is not None:
                return Response()
        except Gameplay.DoesNotExist:
            raise Http404()

        # total up the score
        gameplay.total_score = sum(
            [question.calculate_score() for question in gameplay.questions.all()]
        )
        gameplay.save()

        # create score entry
        game = Game.objects.get(eth_address__iexact=settings.KYM_GAME_ADDRESS)
        PlayerScore.objects.create(game=game, user=user, score=gameplay.total_score)

        # return success
        return Response(data=GameplayResultsSerializer(gameplay).data)


class QuestionViewSet(ViewSet):
    @extend_schema(responses={200: RevealedQuestionSerializer})
    def submit_answer(self, request, question_id: int):
        """Endpoint to submit an answer for a question"""
        # get the user
        user = request.user

        # get the question
        try:
            question = Question.objects.get(id=question_id, gameplay__user=user)
        except Question.DoesNotExist:
            raise Http404()

        # get the answer
        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # update the question
        question.title_answer = serializer.validated_data["title"]
        question.artist_answer = serializer.validated_data["artist"]
        question.supply_answer = serializer.validated_data["supply"]
        question.season_answer = serializer.validated_data["season"]
        question.save()

        # calculate the score
        question.calculate_score()

        # return the question
        return Response(data=RevealedQuestionSerializer(question).data)

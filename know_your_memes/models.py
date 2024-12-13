from django.conf import settings
from django.db import models


class Gameplay(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total_score = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Question(models.Model):
    gameplay = models.ForeignKey(
        Gameplay, related_name="questions", on_delete=models.CASCADE
    )
    token_id = models.IntegerField()
    image_url = models.URLField(max_length=255)
    blurhash = models.CharField(max_length=255)
    color = models.CharField(max_length=10)
    score = models.IntegerField(null=True)

    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    supply = models.IntegerField()
    season = models.IntegerField()

    title_options = models.JSONField()
    artist_options = models.JSONField()
    supply_options = models.JSONField()
    season_options = models.JSONField()

    title_answer = models.CharField(max_length=255, null=True, blank=True)
    artist_answer = models.CharField(max_length=255, null=True, blank=True)
    supply_answer = models.IntegerField(null=True)
    season_answer = models.IntegerField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_score(self) -> int:
        # exit early if already scored
        if self.score is not None:
            return self.score

        # calculate number of correct answers
        answers = [
            self.title_answer,
            self.artist_answer,
            self.supply_answer,
            self.season_answer,
        ]
        correct_answers = [self.title, self.artist, self.supply, self.season]
        num_correct = sum(
            [
                1
                for answer, correct_answer in zip(answers, correct_answers)
                if answer == correct_answer
            ]
        )

        # calculate time remaining
        duration = self.updated_at - self.created_at
        time_remaining = (
            (settings.KYM_GAME_DURATION - duration).total_seconds()
            if duration < settings.KYM_GAME_DURATION
            else 0
        )

        # calculate score
        self.score = int(num_correct * 50 * time_remaining)
        self.save()

        return self.score

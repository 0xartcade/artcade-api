from django.conf import settings
from django.db import models

from utils.rest_framework.validators import bytes32_hex_validator, eth_address_validator


class Game(models.Model):
    """
    Model to capture data needed for games onchain.
    This should only be written to by admins after ensuring games are properly setup.
    """

    name = models.CharField(max_length=1000)
    description = models.TextField()
    eth_address = models.CharField(
        max_length=42,
        unique=True,
        validators=[eth_address_validator],
    )
    url = models.URLField()
    nft_address = models.CharField(
        max_length=42,
        unique=True,
        validators=[eth_address_validator],
    )
    signing_key = models.CharField(max_length=66, validators=[bytes32_hex_validator])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.eth_address = self.eth_address.lower()
        self.nft_address = self.nft_address.lower()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PlayerHighScore(models.Model):
    """
    Model to capture high scores put onchain by users, basically, this is the leaderboard for all games.
    This should only be written to from webhooks.
    """

    # unique constraint on user and game
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "game"], name="unique_user_game"),
        ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.BigIntegerField(default=0)
    token_id = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.game.name}"


class PlayerScore(models.Model):
    """
    Universal model that adheres to the simple onchain standard for storing scores.
    This should never be created by a user but rather from a game app with extra logic around limiting score.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    score = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.game.name} - {self.score}"

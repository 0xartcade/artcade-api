from django.db import models


class Webhook(models.Model):
    webhook_id = models.CharField(max_length=100, unique=True)
    signing_key = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.webhook_id

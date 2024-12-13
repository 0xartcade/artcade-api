from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.rest_framework.validators import eth_address_validator


# build off of the base user and add fields.
# passwords only useable for admins, otherwise people will sign in with eth wallet or OTPs to email
class User(AbstractUser):
    eth_address = models.CharField(
        max_length=42,
        null=True,
        blank=True,
        unique=True,
        validators=[eth_address_validator],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.eth_address:
            self.eth_address = self.eth_address.lower()
        return super().save(*args, **kwargs)


class Nonce(models.Model):
    value = models.CharField(max_length=32, unique=True)
    expires_at = models.DateTimeField()

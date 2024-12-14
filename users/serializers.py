from django.contrib.auth import get_user_model
from rest_framework.serializers import CharField, ModelSerializer, Serializer

from users.models import OTP, Nonce

User = get_user_model()


class NonceSerializer(ModelSerializer):
    class Meta:
        model = Nonce
        fields = ["value"]


class LoginSerializer(Serializer):
    message = CharField()
    signature = CharField()


class OTPSerializer(ModelSerializer):
    class Meta:
        model = OTP
        fields = ["code"]


class OTPLoginSerializer(Serializer):
    code = CharField()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["eth_address", "username", "created_at", "updated_at"]

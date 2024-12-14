from datetime import timedelta
from secrets import token_hex

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.middleware import csrf
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema
from knox.views import LoginView as KnoxLoginView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from siwe import SiweMessage

from users.models import OTP, Nonce
from users.serializers import (
    LoginSerializer,
    NonceSerializer,
    OTPLoginSerializer,
    OTPSerializer,
    UserSerializer,
)

User = get_user_model()


class NonceView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        description="Get a new nonce for SIWE login",
        responses={200: NonceSerializer},
    )
    def get(self, request):
        # create nonce that expires in 5 minutes
        nonce = Nonce.objects.create(
            value=token_hex(settings.NONCE_LENGTH),
            expires_at=now() + settings.NONCE_EXPIRATION,
        )

        return Response(data=NonceSerializer(nonce).data, status=status.HTTP_200_OK)


class LoginView(KnoxLoginView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "expiry": {"type": "string", "format": "date-time"},
                    "user": {
                        "type": "object",
                        "properties": {
                            field: {
                                "type": "string",
                                "format": "date-time"
                                if field == "created_at" or field == "updated_at"
                                else "string",
                            }
                            for field in UserSerializer.Meta.fields
                        },
                    },
                },
            },
        },
    )
    def post(self, request, format=None):
        """Endpoint to login via SIWE"""
        # serializer data
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get info out of the message
        message = SiweMessage.from_message(serializer.validated_data["message"])
        eth_address = message.address.lower()
        nonce_value = message.nonce

        # check nonce
        try:
            nonce = Nonce.objects.get(value=nonce_value)
            if now() > nonce.expires_at:
                return Response(
                    data={
                        "detail": "Nonce expired, please try again",
                        "code": "nonce_expired",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Nonce.DoesNotExist:
            return Response(
                data={"detail": "Invlaid nonce", "code": "invalid_nonce"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # verify signature
        try:
            message.verify(signature=serializer.validated_data["signature"])
        except Exception:
            return Response(
                data={"detail": "Invalid signature", "code": "invalid_signature"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # get/create the user
        user, created = User.objects.get_or_create(eth_address=eth_address)
        if created:
            user.username = user.eth_address
        user.save()

        # login the user
        login(request, user)

        # delete the nonce
        nonce.delete()

        # get csrf token
        csrf.rotate_token(request)

        # get response
        response = super().post(request, format=format)

        # add csrf token to the response as a custom header
        response.headers[settings.CSRF_RET_HEADER_NAME] = request.META["CSRF_COOKIE"]

        # add authentication credentials to the response as cookie
        response.set_cookie(
            key=settings.AUTH_COOKIE_NAME,
            value=response.data["token"],
            httponly=True,
            secure=True,
            samesite="None",
            domain=".0xartcade.xyz",
            expires=response.data["expiry"],  # TODO: figure this out later
        )

        # return response
        return response


class GenerateOTPView(APIView):
    """
    Generate a OTP token for a user to use to link their mobile device for gameplay
    """

    @extend_schema(
        responses={200: OTPSerializer},
    )
    def post(self, request, format=None):
        # generate otp for user
        otp = OTP.objects.create(
            user=request.user,
            code=token_hex(3),
            expires_at=now() + timedelta(minutes=5),
        )

        # return response
        return Response(data=OTPSerializer(otp).data)


class OTPLoginView(KnoxLoginView):
    """Endpoint to login via OTP"""

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=OTPLoginSerializer,
        responses={
            200: {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "expiry": {"type": "string", "format": "date-time"},
                    "user": {
                        "type": "object",
                        "properties": {
                            field: {
                                "type": "string",
                                "format": "date-time"
                                if field == "created_at" or field == "updated_at"
                                else "string",
                            }
                            for field in UserSerializer.Meta.fields
                        },
                    },
                },
            }
        },
    )
    def post(self, request, format=None):
        # get serializer data
        serializer = OTPLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get the otp
        try:
            otp = OTP.objects.get(code=serializer.validated_data["code"])
            if now() > otp.expires_at:
                return Response(
                    data={
                        "detail": "OTP expired, please try again",
                        "code": "otp_expired",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except OTP.DoesNotExist:
            return Response(
                data={"detail": "Invalid OTP", "code": "otp_invalid"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # login the user
        login(request, otp.user)

        # delete the otp
        otp.delete()

        # get csrf token
        csrf.rotate_token(request)

        # get response
        response = super().post(request, format=format)

        # add csrf token to the response as a custom header
        response.headers[settings.CSRF_RET_HEADER_NAME] = request.META["CSRF_COOKIE"]

        # add authentication credentials to the response as cookie
        response.set_cookie(
            key=settings.AUTH_COOKIE_NAME,
            value=response.data["token"],
            httponly=True,
            secure=True,
            samesite="None",
            domain=".0xartcade.xyz",
            expires=response.data["expiry"],  # TODO: figure this out later
        )

        # return response
        return response


class UserInfoView(APIView):
    @extend_schema(responses={200: UserSerializer})
    def get(self, request):
        """Endpoint to get user info, if they are logged in"""
        response = Response(
            data=UserSerializer(request.user).data, status=status.HTTP_200_OK
        )

        # add csrf token to the response as a custom header
        response.headers[settings.CSRF_RET_HEADER_NAME] = csrf.get_token(request)

        return response

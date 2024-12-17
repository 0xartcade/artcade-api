from datetime import timedelta

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from eth_account import Account
from eth_account.messages import encode_defunct
from rest_framework import status
from siwe import SiweMessage

from users.models import OTP, Nonce

User = get_user_model()

pytestmark = [pytest.mark.django_db(transaction=True)]


# test getting the nonce from the backed
def test_get_nonce(api_client):
    nonce_response = api_client.get("/auth/nonce")
    nonce = Nonce.objects.first()
    assert (
        nonce_response.status_code == 200
        and len(nonce_response.data["value"]) == 32
        and nonce.value == nonce_response.data["value"]
    )


# test logging in
def test_login(api_client):
    # create user address and ensure no users
    account = Account.create()
    assert User.objects.count() == 0

    # create user in the backend
    nonce_response = api_client.get(
        "/auth/nonce",
    )
    message = SiweMessage(
        domain="artcade.xyz",
        address=account.address,
        uri="https://artcade.xyz",
        statement="Sign in to access Artcade",
        chain_id=360,
        version="1",
        issued_at=timezone.now().isoformat(),
        nonce=nonce_response.data["value"],
    )
    signature = account.sign_message(
        encode_defunct(text=message.prepare_message())
    ).signature.hex()

    login_response = api_client.post(
        "/auth/login",
        {"message": message.prepare_message(), "signature": signature},
    )

    assert (
        login_response.status_code == status.HTTP_200_OK
        and api_client.cookies[settings.AUTH_COOKIE_NAME].value
        == login_response.data["token"]
        and len(api_client.cookies[settings.CSRF_COOKIE_NAME].value) > 0
        and len(login_response.data["token"]) > 0
        and login_response.data["user"]["eth_address"] == account.address.lower()
        and login_response.data["user"]["username"] == account.address.lower()
        and len(
            User.objects.get(eth_address__iexact=account.address).auth_token_set.all()
        )
        == 1
        and User.objects.count() == 1
        and Nonce.objects.count() == 0
    )

    # login in again, making sure that the user is found and not created
    nonce_response = api_client.get(
        "/auth/nonce",
    )
    message = SiweMessage(
        domain="artcade.xyz",
        address=account.address,
        uri="https://artcade.xyz",
        statement="Sign in to access Artcade",
        chain_id=360,
        version="1",
        issued_at=timezone.now().isoformat(),
        nonce=nonce_response.data["value"],
    )
    signature = account.sign_message(
        encode_defunct(text=message.prepare_message())
    ).signature.hex()
    login_response = api_client.post(
        "/auth/login",
        {"message": message.prepare_message(), "signature": signature},
    )

    assert (
        login_response.status_code == status.HTTP_200_OK
        and api_client.cookies[settings.AUTH_COOKIE_NAME].value
        == login_response.data["token"]
        and len(api_client.cookies[settings.CSRF_COOKIE_NAME].value) > 0
        and len(login_response.data["token"]) > 0
        and login_response.data["user"]["eth_address"] == account.address.lower()
        and login_response.data["user"]["username"] == account.address.lower()
        and len(
            User.objects.get(eth_address__iexact=account.address).auth_token_set.all()
        )
        == 2
        and User.objects.count() == 1
        and Nonce.objects.count() == 0
    )

    # test logout all
    logout_response = api_client.post(
        "/auth/logout-all",
        headers={"Authorization": f"Token {login_response.data['token']}"},
    )
    assert (
        logout_response.status_code == status.HTTP_204_NO_CONTENT
        and len(
            User.objects.get(eth_address__iexact=account.address).auth_token_set.all()
        )
        == 0
    )


# test logging out
def test_logout(auth_client):
    logout_response = auth_client.post("/auth/logout")
    assert (
        logout_response.status_code == status.HTTP_204_NO_CONTENT
        and len(
            User.objects.get(
                eth_address__iexact=auth_client.eth_address
            ).auth_token_set.all()
        )
        == 0
    )


# test generating an OTP
def test_generate_otp(auth_client):
    r = auth_client.post("/auth/generate-otp")
    assert r.status_code == status.HTTP_200_OK and len(r.data["code"]) == 6


def test_login_with_otp(auth_client, api_client):
    r = auth_client.post("/auth/generate-otp")
    code = r.data["code"]

    r = api_client.post("/auth/login/otp", data={"code": code})

    assert (
        r.status_code == 200
        and len(r.data["token"]) > 0
        and r.data["user"]["eth_address"] == auth_client.eth_address
        and OTP.objects.count() == 0
    )


def test_otp_login_nonexistent_otp(auth_client, api_client):
    r = auth_client.post("/auth/generate-otp")
    code = r.data["code"]

    OTP.objects.get(code=code).delete()

    r = api_client.post("/auth/login/otp", data={"code": code})

    assert r.status_code == 400 and r.data["code"] == "otp_invalid"


def test_otp_login_expired_otp(auth_client, api_client):
    r = auth_client.post("/auth/generate-otp")
    code = r.data["code"]

    otp = OTP.objects.get(code=code)
    otp.expires_at = timezone.now() - timedelta(minutes=5)
    otp.save()

    r = api_client.post("/auth/login/otp", data={"code": code})

    assert r.status_code == 400 and r.data["code"] == "otp_expired"


def test_get_user_info_not_logged_in(api_client):
    r = api_client.get("/auth/user-info")
    assert r.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_user_info_logged_in(auth_client):
    r = auth_client.get("/auth/user-info")
    assert (
        r.status_code == status.HTTP_200_OK
        and r.data["eth_address"] == auth_client.eth_address
        and len(r.headers[settings.CSRF_RET_HEADER_NAME]) > 0
    )

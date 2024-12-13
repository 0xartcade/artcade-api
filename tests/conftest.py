import pytest
from django.conf import settings
from django.utils import timezone
from eth_account import Account
from eth_account.messages import encode_defunct
from rest_framework import status
from rest_framework.test import APIClient
from siwe import SiweMessage


class AuthClient(APIClient):
    eth_address: str


@pytest.fixture()
def api_client():
    return APIClient(enforce_csrf_checks=True)


@pytest.fixture()
def auth_client(api_client: APIClient) -> AuthClient:
    account = Account.create()
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

    assert login_response.status_code == status.HTTP_200_OK

    # set auth related values in api_client for ease of use in tests
    api_client.eth_address = login_response.data["user"]["eth_address"]
    api_client.defaults["HTTP_AUTHORIZATION"] = f"TOKEN {login_response.data['token']}"

    # delete cookies set automatically (have a separate test for this)
    del api_client.cookies[settings.AUTH_COOKIE_NAME]
    del api_client.cookies[settings.CSRF_COOKIE_NAME]

    return api_client

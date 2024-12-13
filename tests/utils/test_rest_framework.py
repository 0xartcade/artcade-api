import pytest
from django.core.exceptions import ValidationError

from utils.rest_framework.validators import bytes32_hex_validator, eth_address_validator


@pytest.mark.parametrize(
    ["input", "raises"],
    [
        ("foo", True),
        ("0xF4DB918906946B53C8db2292239aC1c8B94145f6", False),
        ("0xF4DB918906946B53C8db2292239aC1c8B94145f6".lower(), False),
    ],
)
def test_eth_address_validator(input: str, raises: bool):
    if raises:
        with pytest.raises(ValidationError):
            eth_address_validator(input)
    else:
        eth_address_validator(input)


@pytest.mark.parametrize(
    ["input", "raises"],
    [
        ("foo", True),
        ("0xa09c83A1326B727b7b6a810da020f8491127b0ba34871317f4547efb632f9b75", True),
        (
            "0xa09c83a1326a727b7b6a810da020f8491127b0ba34871317f4547efb632f9b75",
            False,
        ),
    ],
)
def test_bytes32_hex_validator(input: str, raises: bool):
    if raises:
        with pytest.raises(ValidationError):
            bytes32_hex_validator(input)
    else:
        bytes32_hex_validator(input)

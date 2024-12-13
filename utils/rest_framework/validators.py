from django.core.validators import RegexValidator

eth_address_validator = RegexValidator(
    regex=r"^0x[a-fA-F0-9]{40}$",
    message="Enter a valid Ethereum address. It should start with 0x followed by 40 hexadecimal characters.",
    code="invalid_eth_address",
)

bytes32_hex_validator = RegexValidator(
    regex=r"^0x[a-f0-9]{64}$",
    message="Enter a valid bytes32 hex value. It should start with 0x followed by 64 lowercase hexadecimal characters.",
    code="invalid_bytes32_hex",
)

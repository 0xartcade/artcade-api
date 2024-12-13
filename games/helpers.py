from django.conf import settings
from eth_account import Account
from eth_account.datastructures import SignedMessage
from web3 import Web3


def sign_score(
    name: str, game_address: str, signing_key: str, player: str, score: int, nonce: str
) -> str:
    """
    Takes in data to sign and returns the EIP-712 signatures
    """
    domain_data = {
        "name": name,
        "version": "1",
        "chainId": int(settings.APP_CHAIN_ID),
        "verifyingContract": Web3.to_checksum_address(game_address),
    }
    message_types = {
        "VerifiedScore": [
            {"name": "player", "type": "address"},
            {"name": "score", "type": "uint256"},
            {"name": "nonce", "type": "bytes32"},
        ]
    }
    message_data = {"player": player, "score": score, "nonce": nonce}

    signed_typed_data: SignedMessage = Account.sign_typed_data(
        signing_key, domain_data, message_types, message_data
    )

    return f"0x{signed_typed_data.signature.hex()}"

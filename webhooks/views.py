import hmac

import structlog
from django.contrib.auth import get_user_model
from django.http import Http404
from eth_abi import decode
from hexbytes import HexBytes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.constants import PLAYER_HIGH_SCORE_TOPIC_0
from games.models import Game, PlayerHighScore
from webhooks.models import Webhook

logger = structlog.getLogger(__name__)

User = get_user_model()


class WebhookApiView(APIView):
    def initial(self, request, *args, **kwargs):
        # get raw body in bytes
        body = request.body

        # get the webhook by id
        try:
            webhook = Webhook.objects.get(webhook_id=request.data["webhookId"])
        except Webhook.DoesNotExist:
            raise Http404()

        # verify webhook signature
        self.verify_signature(body, webhook.signing_key)

    def verify_signature(self, body: bytes, signing_key: str) -> bool:
        signature = self.request.headers.get("x-alchemy-signature")
        hmacc = hmac.HMAC(bytes(signing_key, "utf-8"), body, "sha256")

        if hmacc.digest().hex() != signature:
            logger.error("Invalid signature for webhook request.")

            raise ValidationError("Invalid signature.")


class IndexPlayerHighScoreView(WebhookApiView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Endpoint to index data whenever a player submits a score onchain"""
        """Example payload:
    
        {
            "webhookId": "wh_6l5v7cnr8qidv5fe",
            "id": "whevt_wu0em1hlbdlnnheo",
            "createdAt": "2024-12-16T19:41:47.211Z",
            "type": "GRAPHQL",
            "event": {
                "data": {
                    "block": {
                        "hash": "0xc726b598788c14820dc422a95cc328e7f56316f727e735b1bed7adcd29c9fe4b",
                        "number": 7720973,
                        "timestamp": 1734378106,
                        "logs": [
                            {
                                "data": "0x",
                                "topics": [
                                    "0x324cb0062138d65997c86cd3012489ceb351d602f2f55c7408306e8040c79f3f",
                                    "0x000000000000000000000000181f59eb6490c8bf73d291af0d5a56dc90d7cd8b",
                                    "0x0000000000000000000000000000000000000000000000000000000000000002"
                                ],
                                "index": 1,
                                "account": {
                                    "address": "0x6bd4a37fc5753425fa566103a51fd7355d940d48"
                                },
                                "transaction": {
                                    "hash": "0x927bd72c94aafde7d51da1df4846758d13f016d396ae5ad23e13838ce309b8fc",
                                    "from": {
                                        "address": "0x181f59eb6490c8bf73d291af0d5a56dc90d7cd8b"
                                    },
                                    "to": {
                                        "address": "0xca11bde05977b3631167028862be2a173976ca11"
                                    },
                                    "value": "0x5af3107a4000",
                                    "status": 1
                                }
                            },
                            {
                                "data": "0x",
                                "topics": [
                                    "0xec51f1f19b3cb8ab4176d8a463cb3b7a4bb866380c5ee1c51da9577ad94db00a",
                                    "0x000000000000000000000000181f59eb6490c8bf73d291af0d5a56dc90d7cd8b",
                                    "0x0000000000000000000000000000000000000000000000000000000000000002",
                                    "0x00000000000000000000000000000000000000000000000000000000000003e8"
                                ],
                                "index": 2,
                                "account": {
                                    "address": "0x6bd4a37fc5753425fa566103a51fd7355d940d48"
                                },
                                "transaction": {
                                    "hash": "0x927bd72c94aafde7d51da1df4846758d13f016d396ae5ad23e13838ce309b8fc",
                                    "from": {
                                        "address": "0x181f59eb6490c8bf73d291af0d5a56dc90d7cd8b"
                                    },
                                    "to": {
                                        "address": "0xca11bde05977b3631167028862be2a173976ca11"
                                    },
                                    "value": "0x5af3107a4000",
                                    "status": 1
                                }
                            }
                        ]
                    }
                },
                "sequenceNumber": "10000000006588185002",
                "network": "SHAPE_SEPOLIA"
            }
        }
        """
        # parse the data from the webhook
        logs = request.data["event"]["data"]["block"]["logs"]

        # parse the logs
        for log in logs:
            # ensure it was sent from a registered game
            game_address = log["account"]["address"]
            try:
                game = Game.objects.get(eth_address__iexact=game_address)
            except Game.DoesNotExist:
                continue

            # get or create the player entry
            player_address = decode(["address"], HexBytes(log["topics"][1]))[0]
            token_id = decode(["uint256"], HexBytes(log["topics"][2]))[0]
            user = User.objects.get(eth_address__iexact=player_address)
            phs, _ = PlayerHighScore.objects.get_or_create(
                user=user, game=game, token_id=token_id
            )

            # update with the new high score
            if log["topics"][0] == PLAYER_HIGH_SCORE_TOPIC_0:
                score = decode(["uint256"], HexBytes(log["topics"][3]))[0]
                if score > phs.score:
                    phs.score = score
                    phs.save()

        # return 200
        return Response()


# TODO: Implement global ticket leaderboard later
class IndexTicketsDispensedView(WebhookApiView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Endpoint to index tickets earned whenever a player submits a score onchain"""
        # get the webhook by id

        # verify webhook signature

        # parse the data from the webhook

        # get or create the player entry

        # update model with total tickets earned

        # return 200
        return Response()

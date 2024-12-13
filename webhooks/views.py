from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class WebhookApiView(APIView):
    def verify_signature(self):
        pass


class IndexPlayerHighScoreView(WebhookApiView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Endpoint to index data whenever a player submits a score onchain"""
        # get the webhook by id

        # verify webhook signature

        # parse the data from the webhook

        # ensure it was sent from a registered game

        # get or create the player entry

        # update with the new high score (making sure we aren't indexing old data)

        # return 200
        return Response()


class IndexPlayerRegisteredView(WebhookApiView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Endpoint to index datat whenever a player registers for a game"""
        # get the webhook by id

        # verify webhook signature

        # parse the data from the webhook

        # ensure it was sent from a registered game

        # get or create the player entry

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

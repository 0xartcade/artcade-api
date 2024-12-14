"""
URL configuration for the api.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from knox.views import LogoutAllView, LogoutView

from games.views import (
    GameViewSet,
    LeaderboardViewSet,
    PlayerHighScoreViewSet,
    PlayerScoreViewSet,
    SignScoresView,
)
from know_your_memes.views import GameplayViewset, QuestionViewSet
from users.views import GenerateTokenView, LoginView, NonceView, UserInfoView

from . import views as api_views

urlpatterns = [
    #
    # General
    #
    path("", api_views.index),
    path("robots.txt", api_views.robots),
    path("favicon.ico", api_views.favicon),
    path("health", api_views.health),
    path("admin", admin.site.urls),
    #
    # API docs
    #
    path("docs", SpectacularSwaggerView.as_view(url_name="schema")),
    path("docs/schema", SpectacularAPIView.as_view(), name="schema"),
    #
    # Auth
    #
    path("auth/nonce", NonceView.as_view()),
    path("auth/login", LoginView.as_view()),
    path("auth/generate-token", GenerateTokenView.as_view()),
    path("auth/logout", LogoutView.as_view()),
    path("auth/logout-all", LogoutAllView.as_view()),
    path("auth/user-info", UserInfoView.as_view()),
    #
    # Games
    #
    path("games", GameViewSet.as_view({"get": "list"})),
    path("games/<int:pk>", GameViewSet.as_view({"get": "retrieve"})),
    #
    # Leaderboard
    #
    path("leaderboard/<int:game_id>", LeaderboardViewSet.as_view({"get": "list"})),
    #
    # Player High Scores
    #
    path("high-scores", PlayerHighScoreViewSet.as_view({"get": "list"})),
    path(
        "high-scores/<int:game_id>",
        PlayerHighScoreViewSet.as_view({"get": "retrieve"}),
    ),
    #
    # Player Scores
    #
    path("scores", PlayerScoreViewSet.as_view({"get": "list"})),
    path("scores/sign", SignScoresView.as_view()),
    #
    # Know Your Memes
    #
    path("kym/gameplay", GameplayViewset.as_view({"post": "create_gameplay"})),
    path(
        "kym/gameplay/<int:gameplay_id>/question",
        GameplayViewset.as_view({"post": "create_question"}),
    ),
    path(
        "kym/gameplay/<int:gameplay_id>/submit",
        GameplayViewset.as_view({"post": "submit_gameplay"}),
    ),
    path(
        "kym/question/<int:question_id>/submit",
        QuestionViewSet.as_view({"post": "submit_answer"}),
    ),
]

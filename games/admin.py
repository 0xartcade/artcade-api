from django.contrib import admin

from .models import Game, PlayerHighScore


class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "description", "url")}),
        ("Web3", {"fields": ("eth_address", "nft_address", "signing_key")}),
        (
            "Metadata",
            {"fields": readonly_fields},
        ),
    )


class PlayerHighScoreAdmin(admin.ModelAdmin):
    list_display = ("id", "user__username", "game__name", "score", "token_id")
    list_filter = ("game__name",)
    sortable_by = ("score",)
    search_fields = ("user__username", "game__name", "token_id")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("user", "game", "score", "token_id")}),
        (
            "Metadata",
            {"fields": readonly_fields},
        ),
    )


admin.site.register(Game, GameAdmin)
admin.site.register(PlayerHighScore, PlayerHighScoreAdmin)

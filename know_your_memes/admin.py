from django.contrib import admin

from .models import Gameplay, Question


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("token_id", "image_url", "blurhash", "color")}),
        ("Source of Trutch", {"fields": ("title", "artist", "supply", "season")}),
        (
            "Options",
            {
                "fields": (
                    "title_options",
                    "artist_options",
                    "supply_options",
                    "season_options",
                )
            },
        ),
        (
            "Answers",
            {
                "fields": (
                    "title_answer",
                    "artist_answer",
                    "supply_answer",
                    "season_answer",
                )
            },
        ),
        ("Metadata", {"fields": readonly_fields}),
    )


class GameplayAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "total_score")
    search_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("user", "total_score")}),
        (
            "Metadata",
            {"fields": readonly_fields},
        ),
    )
    inlines = [QuestionInline]


admin.site.register(Gameplay, GameplayAdmin)

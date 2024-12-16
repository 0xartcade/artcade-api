from django.contrib import admin

from .models import Webhook


class WebhookAdmin(admin.ModelAdmin):
    list_display = ("webhook_id",)


admin.site.register(Webhook)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import OTP, Nonce, User


class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Web3",
            {"fields": ("eth_address",)},
        ),
        (
            "Permissions",
            {"fields": ("is_staff", "is_active", "groups", "user_permissions")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
    )
    search_fields = ("username",)
    ordering = ("id",)


class NonceAdmin(admin.ModelAdmin):
    list_display = ("value", "expires_at")


class OTPAdmin(admin.ModelAdmin):
    list_display = ("user__username", "code", "expires_at")


admin.site.register(User, CustomUserAdmin)
admin.site.register(Nonce, NonceAdmin)
admin.site.register(OTP, OTPAdmin)

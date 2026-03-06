from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, OTPRequest


class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        "id",
        "email",
        "username",
        "is_verified",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    list_filter = (
        "is_verified",
        "is_staff",
        "is_superuser",
        "is_active",
    )

    search_fields = ("email", "username")
    ordering = ("email",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Custom Fields", {
            "fields": ("is_verified",),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Custom Fields", {
            "fields": ("is_verified",),
        }),
    )


admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "full_name",
        "topic_interests",
    )

    search_fields = (
        "user__email",
        "full_name",
        "topic_interests",
    )


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "get_email",
        "masked_otp",
        "created_at",
        "expiration_time",
        "is_expired",
    )

    list_filter = (
        "created_at",
        "expiration_time",
        "user",
    )

    search_fields = (
        "user__email",
        "email",
        "otp",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "expiration_time",
    )

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Email"

    def masked_otp(self, obj):
        if obj.otp:
            return obj.otp[:6] + "****"
        return "-"
    masked_otp.short_description = "OTP"

    def is_expired(self, obj):
        return obj.is_expired()
    is_expired.boolean = True
    is_expired.short_description = "Expired"
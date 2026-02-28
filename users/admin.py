from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone

from .models import User, UserProfile, OTPRequest


# USER ADMIN 
@admin.register(User)
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
    ordering = ("email", )

    # IMPORTANT: Do NOT append BaseUserAdmin.fieldsets
    # Redefine cleanly for Jazzmin tabs to work
    fieldsets = (
        ("General", {
            "fields": ("email", "username", "password"),
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            ),
        }),
        ("Verification", {
            "fields": ("is_verified", ),
        }),
        ("Important dates", {
            "fields": ("last_login", "date_joined"),
        }),
    )

    add_fieldsets = (
        ("General", {
            "classes": ("wide", ),
            "fields": ("email", "username", "password1", "password2"),
        }),
        ("Verification", {
            "fields": ("is_verified", ),
        }),
    )


# USER PROFILE ADMIN
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "full_name")
    search_fields = ("user__email", "full_name")
    list_select_related = ("user", )


# OTP REQUEST ADMIN 
@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
        "expiration_time",
        "is_used",
        "expired_status",
    )

    list_filter = (
        "is_used",
        "created_at",
        "expiration_time",
    )

    search_fields = ("user__email", )
    ordering = ("-created_at", )

    readonly_fields = (
        "user",
        "otp_hash",
        "created_at",
        "expiration_time",
        "is_used",
    )

    def expired_status(self, obj):
        if timezone.now() > obj.expiration_time:
            return format_html(
                '<span style="color:#dc3545;font-weight:bold;">Expired</span>')
        return format_html(
            '<span style="color:#28a745;font-weight:bold;">Valid</span>')

    expired_status.short_description = "Status"

    # Prevent manual tampering
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

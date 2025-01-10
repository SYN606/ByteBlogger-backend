from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


# Custom User Admin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('id', 'email', 'username', 'is_verified', 'is_staff', 'is_superuser')
    list_filter = ('is_verified', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)

    # Fields to display when viewing a user in the admin
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fields to display when adding a new user in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'is_verified', 'is_staff', 'is_superuser'),
        }),
    )


# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'topic_interests')
    search_fields = ('user__email', 'full_name', 'topic_interests')
    list_filter = ('full_name',)

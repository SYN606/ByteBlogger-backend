from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.apps import apps


def create_author_group(sender, **kwargs):
    if sender == apps.get_app_config('blog'):
        author_group, created = Group.objects.get_or_create(name="Author")
        permissions = Permission.objects.filter(
            codename__in=['add_post', 'change_post', 'delete_post'])
        author_group.permissions.set(permissions)
        print("Author group ensured on migration.")


post_migrate.connect(create_author_group)

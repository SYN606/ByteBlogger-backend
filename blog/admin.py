from django.contrib import admin
from .models import Blog, Category


class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'slug', 'short_description', 'category',
                    'body', 'image')
    search_fields = ('title', 'category__name', 'author__username')
    prepopulated_fields = {'slug': ('title', )}


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    search_fields = ('name', )


admin.site.register(Blog, BlogAdmin)
admin.site.register(Category, CategoryAdmin)

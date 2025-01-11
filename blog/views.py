from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Blog, Category


def all_blogs(request):
    """
    Route: /blog/
    Display all blogs with title, short description, category, and slug.
    """
    blogs = Blog.objects.all().values('title', 'short_description',
                                      'category__name', 'slug')
    return JsonResponse(list(blogs), safe=False)


def blog_detail(request, slug):
    """
    Route: /blog/<blog_title_slug>/
    Get the blog based on the title slug and return all the blog details.
    """
    blog = get_object_or_404(Blog, slug=slug)
    blog_data = {
        'title': blog.title,
        'short_description': blog.short_description,
        'body': blog.body,
        'category': blog.category.name,
        'slug': blog.slug,
        'author': blog.author.username,
        'image': blog.image.url if blog.image else None
    }
    return JsonResponse(blog_data)


def blogs_by_category(request, category_slug):
    """
    Route: /blog/cat-<category_slug>/
    Return all blogs within a category with title, short description, and slug.
    """
    category = get_object_or_404(Category, slug=category_slug)
    blogs = Blog.objects.filter(category=category).values(
        'title', 'short_description', 'slug')
    return JsonResponse(list(blogs), safe=False)

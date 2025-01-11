from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_blogs, name='all_blogs'),  # List all blogs
    path('<slug:slug>/', views.blog_detail,
         name='blog_detail'),  # Single blog detail based on the slug
    path('category/<slug:category_slug>/',
         views.blogs_by_category,
         name='blogs_by_category'),  # Blogs by category
]

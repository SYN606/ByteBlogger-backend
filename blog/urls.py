from django.urls import path
from .views import BlogListView, BlogDetailView, BlogByCategoryView, CommentCreateView

urlpatterns = [
    path('blog/', BlogListView.as_view(), name='blog-list'
         ),  # GET all blogs / POST new blog (only authors/admins)
    path('blog/<slug:slug>/', BlogDetailView.as_view(),
         name='blog-detail'),  # GET single blog
    path('blog/cat-<slug:category_slug>/',
         BlogByCategoryView.as_view(),
         name='blogs-by-category'),  # GET blogs in category
    path('blog/<slug:slug>/comment/',
         CommentCreateView.as_view(),
         name='add-comment'),  # POST comment
]

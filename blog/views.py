from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from .models import Blog, Category, Comment
from .serializers import BlogSerializer, CommentSerializer
from django.contrib.auth.models import Group


class BlogListView(APIView):
    """
    Route: /blog/
    GET: Get all blogs (title, short description, category, and slug).
    POST: Create a new blog (only for authors & admins).
    """

    permission_classes = [permissions.IsAuthenticated
                          ]  # Only logged-in users can post

    def get(self, request):
        blogs = Blog.objects.all().values('title', 'short_description',
                                          'category__name', 'slug')
        return Response(blogs, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Only users who are in the "Author" group or are admins can create blogs.
        """
        if not request.user.is_superuser:  # Admins can always create blogs
            author_group = Group.objects.get(
                name="Author")  # Fetch the "Author" group
            if not author_group in request.user.groups.all(
            ):  # Check user membership
                return Response(
                    {'error': 'You do not have permission to create a blog.'},
                    status=status.HTTP_403_FORBIDDEN)

        serializer = BlogSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                author=request.user)  # Assign logged-in user as the author
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlogDetailView(APIView):
    """
    Route: /blog/<blog_slug>/
    Get details of a single blog, including comments.
    """

    def get(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        comments = Comment.objects.filter(blog=blog)

        blog_data = {
            'title': blog.title,
            'short_description': blog.short_description,
            'body': blog.body,
            'category': blog.category.name,
            'slug': blog.slug,
            'author': blog.author.username,
            'image': blog.image.url if blog.image else None,
            'comments': CommentSerializer(comments,
                                          many=True).data  # Include comments
        }
        return Response(blog_data, status=status.HTTP_200_OK)


class BlogByCategoryView(APIView):
    """
    Route: /blog/cat-<category_slug>/
    Get all blogs within a category with title, short description, and slug.
    """

    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        blogs = Blog.objects.filter(category=category).values(
            'title', 'short_description', 'slug')
        return Response(blogs, status=status.HTTP_200_OK)


class CommentCreateView(APIView):
    """
    Route: /blog/<blog_slug>/comment/
    Allows users to add comments to a blog post.
    """

    permission_classes = [permissions.IsAuthenticated
                          ]  # Only logged-in users can comment

    def post(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user,
                            blog=blog)  # Auto-assign user & blog
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

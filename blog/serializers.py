from rest_framework import serializers
from .models import Blog, Category


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'description',
                  'slug'] 


class BlogSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'short_description', 'slug', 'author', 'body',
            'image', 'category'
        ] 

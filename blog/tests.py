import random
from django.contrib.auth import get_user_model
from .models import Blog, Category  # Replace 'myapp' with your actual app name
from django.utils.text import slugify
from faker import Faker
from django.conf import settings

# Initialize Faker to generate fake data
fake = Faker()

# Create sample categories
categories = [
    'Technology', 'Health', 'Lifestyle', 'Travel', 'Education', 'Business',
    'Food', 'Entertainment', 'Science', 'Sports'
]
category_instances = []

# Create Categories
for category_name in categories:
    category, created = Category.objects.get_or_create(
        name=category_name, slug=slugify(category_name))
    category_instances.append(category)

# Get a staff user to assign as the author for blogs
User = get_user_model(
)  # Get the custom user model defined in settings.AUTH_USER_MODEL
user = User.objects.filter(
    is_staff=True).first()  # Ensure there's at least one staff user

if not user:
    print("No staff user found. Please create a staff user.")
else:
    # Create 10 blogs
    for _ in range(10):
        title = fake.sentence(nb_words=5)  # Fake title
        short_description = fake.text(
            max_nb_chars=150)  # Fake short description
        body = fake.text(max_nb_chars=1000)  # Fake body content
        category = random.choice(
            category_instances)  # Randomly select a category for the blog

        # Create the Blog instance
        blog = Blog.objects.create(
            title=title,
            short_description=short_description,
            body=body,
            category=category,
            author=user  # Assign the staff user as the author
        )
        print(f"Created blog: {title}, Category: {category.name}")

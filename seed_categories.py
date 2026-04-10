import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blog.settings')
django.setup()

from blog_app.models import Category

categories = [
    {'name': 'Python', 'slug': 'python', 'order': 1, 'color': '#3776ab'},
    {'name': 'Django', 'slug': 'django', 'order': 2, 'color': '#092e20'},
    {'name': 'Web Dev', 'slug': 'web-dev', 'order': 3, 'color': '#61dbfb'},
    {'name': 'AI & ML', 'slug': 'ai-ml', 'order': 4, 'color': '#f2d349'},
    {'name': 'DevOps', 'slug': 'devops', 'order': 5, 'color': '#2496ed'},
]

for cat_data in categories:
    cat, created = Category.objects.get_or_create(
        slug=cat_data['slug'],
        defaults={'name': cat_data['name'], 'order': cat_data['order'], 'color': cat_data['color']}
    )
    if not created:
        cat.name = cat_data['name']
        cat.order = cat_data['order']
        cat.color = cat_data['color']
        cat.save()
    print(f"Category '{cat.name}' is ready.")

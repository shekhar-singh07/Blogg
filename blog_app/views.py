from django.shortcuts import render, redirect
from .models import Post
from django.contrib.auth.decorators import login_required

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        Post.objects.create(
            title=title,
            content=content,
            author=request.user
        )
        return redirect('home')
    return render(request, 'create_post.html')
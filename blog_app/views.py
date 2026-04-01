from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q
from .models import Post, Like, Comment


def home(request):
    posts = Post.objects.all()
    query = request.GET.get('q', '').strip()
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )
    # Track which posts the current user has liked
    if request.user.is_authenticated:
        liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    else:
        liked_post_ids = []
    return render(request, 'home.html', {
        'posts': posts,
        'liked_post_ids': list(liked_post_ids),
        'search_query': query,
    })


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = post.likes.filter(user=request.user).exists()
    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'user_has_liked': user_has_liked,
    })


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
        messages.success(request, 'Post published successfully!')
        return redirect('home')
    return render(request, 'create_post.html')


@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You can only edit your own posts.")
    if request.method == "POST":
        post.title = request.POST['title']
        post.content = request.POST['content']
        post.save()
        messages.success(request, 'Post updated successfully!')
        return redirect('post_detail', pk=post.pk)
    return render(request, 'update_post.html', {'post': post})


@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return HttpResponseForbidden("You can only delete your own posts.")
    if request.method == "POST":
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return render(request, 'delete_post.html', {'post': post})


@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    if not created:
        like.delete()
    next_url = request.GET.get('next', 'home')
    if next_url == 'detail':
        return redirect('post_detail', pk=pk)
    return redirect('home')


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
            )
            messages.success(request, 'Comment posted!')
    return redirect('post_detail', pk=pk)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if comment.author != request.user:
        return HttpResponseForbidden("You can only delete your own comments.")
    post_pk = comment.post.pk
    if request.method == "POST":
        comment.delete()
        messages.success(request, 'Comment deleted.')
    return redirect('post_detail', pk=post_pk)


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'registration/register.html')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'registration/register.html')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return render(request, 'registration/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken.')
            return render(request, 'registration/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, f'Welcome to DevBlog, {username}!')
        return redirect('home')

    return render(request, 'registration/register.html')
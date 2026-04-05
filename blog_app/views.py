from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Post, Like, Comment, Category, Tag, Bookmark, Profile


def home(request):
    # Only show published posts to public, let users see their own drafts
    if request.user.is_authenticated:
        posts = Post.objects.filter(Q(status='published') | Q(author=request.user))
    else:
        posts = Post.objects.filter(status='published')

    # Search
    query = request.GET.get('q', '').strip()
    if query:
        posts = posts.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

    # Categories for sidebar
    categories = Category.objects.all()

    # Pagination
    paginator = Paginator(posts, 8) # 8 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Track user interactions
    liked_post_ids = []
    bookmarked_post_ids = []
    if request.user.is_authenticated:
        liked_post_ids = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
        bookmarked_post_ids = list(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    return render(request, 'home.html', {
        'page_obj': page_obj,
        'categories': categories,
        'liked_post_ids': liked_post_ids,
        'bookmarked_post_ids': bookmarked_post_ids,
        'search_query': query,
    })


def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    if request.user.is_authenticated:
        posts = Post.objects.filter(category=category).filter(Q(status='published') | Q(author=request.user))
    else:
        posts = Post.objects.filter(category=category, status='published')

    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    
    liked_post_ids = []
    bookmarked_post_ids = []
    if request.user.is_authenticated:
        liked_post_ids = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
        bookmarked_post_ids = list(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    return render(request, 'home.html', {
        'page_obj': page_obj,
        'category_filter': category,
        'categories': categories,
        'liked_post_ids': liked_post_ids,
        'bookmarked_post_ids': bookmarked_post_ids,
    })


def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    if request.user.is_authenticated:
        posts = tag.posts.filter(Q(status='published') | Q(author=request.user))
    else:
        posts = tag.posts.filter(status='published')

    paginator = Paginator(posts, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    
    liked_post_ids = []
    bookmarked_post_ids = []
    if request.user.is_authenticated:
        liked_post_ids = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
        bookmarked_post_ids = list(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    return render(request, 'home.html', {
        'page_obj': page_obj,
        'tag_filter': tag,
        'categories': categories,
        'liked_post_ids': liked_post_ids,
        'bookmarked_post_ids': bookmarked_post_ids,
    })


def popular_posts(request):
    posts = Post.objects.filter(status='published').annotate(like_count=Count('likes')).order_by('-like_count')[:10]
    
    categories = Category.objects.all()
    liked_post_ids = []
    bookmarked_post_ids = []
    if request.user.is_authenticated:
        liked_post_ids = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
        bookmarked_post_ids = list(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))

    return render(request, 'popular.html', {
        'posts': posts,
        'categories': categories,
        'liked_post_ids': liked_post_ids,
        'bookmarked_post_ids': bookmarked_post_ids,
    })


@login_required
def bookmarked_posts(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    posts = [b.post for b in bookmarks]

    categories = Category.objects.all()
    liked_post_ids = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
    bookmarked_post_ids = [p.id for p in posts]

    return render(request, 'bookmarks.html', {
        'posts': posts,
        'categories': categories,
        'liked_post_ids': liked_post_ids,
        'bookmarked_post_ids': bookmarked_post_ids,
    })


def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    if request.user == profile_user:
        posts = Post.objects.filter(author=profile_user)
    else:
        posts = Post.objects.filter(author=profile_user, status='published')
        
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    liked_post_ids = []
    bookmarked_post_ids = []
    if request.user.is_authenticated:
        liked_post_ids = list(Like.objects.filter(user=request.user).values_list('post_id', flat=True))
        bookmarked_post_ids = list(Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True))
        
    total_likes_received = Like.objects.filter(post__author=profile_user).count()

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'page_obj': page_obj,
        'total_posts': posts.count(),
        'total_likes_received': total_likes_received,
        'liked_post_ids': liked_post_ids,
        'bookmarked_post_ids': bookmarked_post_ids,
    })


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        bio = request.POST.get('bio', '')
        avatar = request.FILES.get('avatar')
        
        profile.bio = bio
        if avatar:
            profile.avatar = avatar
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('user_profile', username=request.user.username)
        
    return render(request, 'edit_profile.html', {'profile': profile})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.status == 'draft' and post.author != request.user:
        return HttpResponseForbidden("This post is not published yet.")
        
    # Get top-level comments (not replies)
    comments = post.comments.filter(parent__isnull=True)
    
    user_has_liked = False
    user_has_bookmarked = False
    if request.user.is_authenticated:
        user_has_liked = post.likes.filter(user=request.user).exists()
        user_has_bookmarked = post.bookmarks.filter(user=request.user).exists()
        
    # Related posts (matching category or tags)
    related_posts = []
    if post.category:
        related_posts = Post.objects.filter(category=post.category, status='published').exclude(pk=post.pk)[:3]

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'user_has_liked': user_has_liked,
        'user_has_bookmarked': user_has_bookmarked,
        'related_posts': related_posts,
    })


@login_required
def create_post(request):
    categories = Category.objects.all()
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']
        category_id = request.POST.get('category')
        tags_str = request.POST.get('tags', '')
        status = request.POST.get('status', 'draft')
        cover_image = request.FILES.get('cover_image')
        
        category = Category.objects.get(id=category_id) if category_id else None
        
        post = Post.objects.create(
            title=title,
            content=content,
            author=request.user,
            category=category,
            status=status,
            cover_image=cover_image
        )
        
        # Process tags
        if tags_str:
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)
                
        if status == 'published':
            messages.success(request, 'Post published successfully!')
        else:
            messages.success(request, 'Post saved to drafts.')
        return redirect('home')
        
    return render(request, 'create_post.html', {'categories': categories})


@login_required
def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    categories = Category.objects.all()
    
    if post.author != request.user:
        return HttpResponseForbidden("You can only edit your own posts.")
        
    if request.method == "POST":
        post.title = request.POST['title']
        post.content = request.POST['content']
        post.status = request.POST.get('status', 'draft')
        
        category_id = request.POST.get('category')
        post.category = Category.objects.get(id=category_id) if category_id else None
        
        cover_image = request.FILES.get('cover_image')
        if cover_image:
            post.cover_image = cover_image
            
        post.save()
        
        # Process tags
        tags_str = request.POST.get('tags', '')
        post.tags.clear()
        if tags_str:
            tag_names = [t.strip() for t in tags_str.split(',') if t.strip()]
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                post.tags.add(tag)
                
        messages.success(request, 'Post updated successfully!')
        return redirect('post_detail', pk=post.pk)
        
    tags_str = ', '.join([t.name for t in post.tags.all()])
    return render(request, 'update_post.html', {
        'post': post, 
        'categories': categories,
        'tags_str': tags_str,
    })


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
def toggle_bookmark(request, pk):
    post = get_object_or_404(Post, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(post=post, user=request.user)
    if not created:
        bookmark.delete()
        messages.success(request, 'Removed from bookmarks.')
    else:
        messages.success(request, 'Saved to bookmarks.')
        
    next_url = request.GET.get('next', 'home')
    if next_url == 'detail':
        return redirect('post_detail', pk=pk)
    if next_url == 'bookmarks':
        return redirect('bookmarked_posts')
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
def reply_comment(request, pk, parent_id):
    post = get_object_or_404(Post, pk=pk)
    parent_comment = get_object_or_404(Comment, pk=parent_id)
    if request.method == "POST":
        content = request.POST.get('content', '').strip()
        if content:
            Comment.objects.create(
                post=post,
                author=request.user,
                parent=parent_comment,
                content=content,
            )
            messages.success(request, 'Reply posted!')
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
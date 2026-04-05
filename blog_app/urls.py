from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('popular/', views.popular_posts, name='popular_posts'),
    path('bookmarks/', views.bookmarked_posts, name='bookmarked_posts'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    
    path('create/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/update/', views.update_post, name='update_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/comment/<int:parent_id>/reply/', views.reply_comment, name='reply_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
]
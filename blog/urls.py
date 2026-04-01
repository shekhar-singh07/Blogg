from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from blog_app import views as blog_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # your app routes
    path('', include('blog_app.urls')),

    # authentication routes
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', blog_views.register, name='register'),
]
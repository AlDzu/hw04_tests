# from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    path('', include('posts.urls', namespace='posts')),
]

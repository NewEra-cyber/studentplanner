"""
URL configuration for productivity_app project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import dashboard, profile_page, manage_activities, activities_resources
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('profile/', profile_page, name='profile'),
    path('activities/', manage_activities, name='manage_activities'),
    path('activities/resources/', activities_resources, name='activities_resources'),
    path('api/', include('api.urls')),
    path('notifications/', include('notifications.urls')),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.adapters import oauth2_login, oauth2_callback

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Include allauth URLs
    path('accounts/spotify/login/', oauth2_login, name='spotify_login'),
    path('accounts/spotify/callback/', oauth2_callback, name='spotify_callback'),
    path('', include('core.urls')),  # Include core app's URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
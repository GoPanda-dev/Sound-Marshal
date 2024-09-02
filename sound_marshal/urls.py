from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.adapters import oauth2_login, oauth2_callback
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Include core app's URLs
    path('api/', include('api.urls')),
    path('api-token-auth/', obtain_auth_token),
    path('accounts/', include('allauth.urls')),  # Include allauth URLs
    path('accounts/spotify/login/', oauth2_login, name='spotify_login'),
    path('accounts/spotify/callback/', oauth2_callback, name='spotify_callback'),
]

handler404 = 'core.views.custom_404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
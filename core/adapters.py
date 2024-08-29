from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect, render
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2LoginView, OAuth2CallbackView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from django.urls import reverse
from requests.auth import HTTPBasicAuth
import requests
from allauth.socialaccount.models import SocialApp, SocialToken
from django.shortcuts import get_object_or_404
from allauth.socialaccount.helpers import complete_social_login
import logging

logger = logging.getLogger(__name__)

class SpotifyOAuth2Adapter(OAuth2Adapter):
    provider_id = 'spotify'
    access_token_url = 'https://accounts.spotify.com/api/token'
    authorize_url = 'https://accounts.spotify.com/authorize'
    profile_url = 'https://api.spotify.com/v1/me'
    playlists_url = 'https://api.spotify.com/v1/me/playlists'

    def get_authorize_params(self, request, app):
        params = super().get_authorize_params(request, app)
        params['show_dialog'] = 'true'
        return params

    def get_default_scope(self):
        return ['user-read-email', 'user-read-private', 'playlist-read-private', 'playlist-read-collaborative']

    def complete_login(self, request, app, token, **kwargs):
        headers = {'Authorization': f'Bearer {token.token}'}
        response = requests.get(self.profile_url, headers=headers)
        response.raise_for_status()
        extra_data = response.json()

        # Fetch user's playlists
        playlists_response = requests.get(self.playlists_url, headers=headers)
        playlists_response.raise_for_status()
        playlists_data = playlists_response.json()
        extra_data['playlists'] = playlists_data.get('items', [])

        social_login = self.get_provider().sociallogin_from_response(request, extra_data)
        return social_login

    def complete_social_login(self, request, app, token, response, **kwargs):
        social_login = self.complete_login(request, app, token, **kwargs)

        if isinstance(social_login, ImmediateHttpResponse):
            return social_login

        # Retrieve the associated social app
        social_app = get_object_or_404(SocialApp, provider=self.provider_id)

        # Find existing social token or create a new one
        social_token, created = SocialToken.objects.get_or_create(
            account=social_login.account,
            app=social_app,
            defaults={
                'token': response['access_token'],
                'token_secret': response.get('refresh_token'),
                'expires_at': self.parse_expiration(response['expires_in']),
            }
        )

        # Update the token and refresh token if already exists
        if not created:
            social_token.token = response['access_token']
            social_token.token_secret = response.get('refresh_token', social_token.token_secret)
            social_token.expires_at = self.parse_expiration(response['expires_in'])
            social_token.save()

        return complete_social_login(request, social_login)
    
    def exchange_code_for_token(self, code, app, redirect_uri):
        """
        Exchange the authorization code for an access token and refresh token.
        """
        client_id = app.client_id
        client_secret = app.secret
        auth_header = HTTPBasicAuth(client_id, client_secret)

        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(self.access_token_url, data=data, headers=headers, auth=auth_header)
        response.raise_for_status()

        token_data = response.json()
        return token_data

    def refresh_access_token(self, refresh_token, app):
        """
        Refresh the access token using the refresh token.
        """
        client_id = app.client_id
        client_secret = app.secret
        auth_header = HTTPBasicAuth(client_id, client_secret)

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(self.access_token_url, data=data, headers=headers, auth=auth_header)
        response.raise_for_status()

        return response.json()

    def get_callback_url(self, request, app):
        return request.build_absolute_uri(reverse('spotify_callback'))

oauth2_login = OAuth2LoginView.adapter_view(SpotifyOAuth2Adapter)
oauth2_callback = OAuth2CallbackView.adapter_view(SpotifyOAuth2Adapter)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if request.user.is_authenticated:
            # If the user is logged in, link the social account
            sociallogin.connect(request, request.user)
            # Redirect the user back to the connections page
            raise ImmediateHttpResponse(redirect('socialaccount_connections'))
        else:
            # Handle the case where the user is not logged in
            pass

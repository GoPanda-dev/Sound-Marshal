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
from allauth.socialaccount.models import SocialApp
from django.shortcuts import get_object_or_404
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialToken
import logging

logger = logging.getLogger(__name__)

class SpotifyOAuth2Adapter(OAuth2Adapter):
    provider_id = 'spotify'
    access_token_url = 'https://accounts.spotify.com/api/token'
    authorize_url = 'https://accounts.spotify.com/authorize'
    profile_url = 'https://api.spotify.com/v1/me'
    playlists_url = 'https://api.spotify.com/v1/me/playlists'  # URL to get user's playlists

    def get_authorize_params(self, request, app):
        params = super().get_authorize_params(request, app)
        params['show_dialog'] = 'true'
        return params

    def get_default_scope(self):
        # Add the scopes that are required to access the playlists
        return ['user-read-email', 'user-read-private', 'playlist-read-private', 'playlist-read-collaborative']

    def complete_login(self, request, app, token, **kwargs):
        try:
            headers = {'Authorization': f'Bearer {token.token}'}
            logger.debug(f"Making request to Spotify API with token: {token.token}")
            response = requests.get(self.profile_url, headers=headers)
            logger.debug(f"Spotify API response status code: {response.status_code}")
            response.raise_for_status()  # This will raise an HTTPError for bad responses
            extra_data = response.json()

            # Fetch user's playlists
            playlists_response = requests.get(self.playlists_url, headers=headers)
            playlists_response.raise_for_status()
            playlists_data = playlists_response.json()

            # Attach playlists data to the extra_data
            extra_data['playlists'] = playlists_data.get('items', [])

            logger.debug(f"Spotify API response data: {extra_data}")
            social_login = self.get_provider().sociallogin_from_response(request, extra_data)
            logger.debug("SocialLogin object created successfully.")
            return social_login
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during Spotify login: {e.response.status_code} - {e.response.text}")
            raise ImmediateHttpResponse(redirect('socialaccount_connections'))
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during Spotify login: {e}")
            raise ImmediateHttpResponse(redirect('socialaccount_connections'))

    def complete_social_login(self, request, app, token, response, **kwargs):
        social_login = self.complete_login(request, app, token, **kwargs)
        
        # If there is an error, it would have been handled in complete_login
        if isinstance(social_login, ImmediateHttpResponse):
            return social_login
        
        logger.debug("Calling complete_social_login to finalize the account connection.")
        return complete_social_login(request, social_login)

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

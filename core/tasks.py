from celery import shared_task
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
import requests
import logging

logger = logging.getLogger(__name__)

@shared_task
def refresh_spotify_tokens():
    spotify_app = SocialApp.objects.get(provider='spotify')
    
    for account in SocialAccount.objects.filter(provider='spotify'):
        token = SocialToken.objects.get(account=account, app=spotify_app)
        refresh_token = token.token_secret

        refresh_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': spotify_app.client_id,
            'client_secret': spotify_app.secret,
        }

        response = requests.post('https://accounts.spotify.com/api/token', data=refresh_data)
        if response.status_code == 200:
            new_token_data = response.json()
            token.token = new_token_data['access_token']
            token.token_secret = new_token_data.get('refresh_token', refresh_token)  # Sometimes Spotify doesn't return a new refresh token
            token.save()

            # Optionally, update user data here using the new access token
            headers = {'Authorization': f'Bearer {token.token}'}
            profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            playlists_response = requests.get('https://api.spotify.com/v1/me/playlists', headers=headers)

            if profile_response.status_code == 200 and playlists_response.status_code == 200:
                profile_data = profile_response.json()
                playlists_data = playlists_response.json()
                
                # Update your model with the new data if needed
                logger.debug(f"Updated Spotify data for user {account.user.username}: {profile_data}, Playlists: {playlists_data}")

        else:
            logger.error(f"Failed to refresh Spotify token for user {account.user.username}: {response.status_code} - {response.text}")

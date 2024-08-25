from allauth.socialaccount.providers.oauth2.provider import OAuth2Provider

class SpotifyProvider(OAuth2Provider):
    id = "spotify"
    name = "Spotify"
    account_class = None  # Use the default SocialAccount class

    def extract_uid(self, data):
        return str(data["id"])

    def extract_common_fields(self, data):
        return dict(email=data.get("email"), username=data.get("id"))

    def get_default_scope(self):
        return ["user-read-email", "user-read-private"]

import workos
from workos.types import sso
from django.conf import settings

# Initialize WorkOS client
workos.api_key = settings.WORKOS_API_KEY
workos.client_id = settings.WORKOS_CLIENT_ID


def get_authorization_url(redirect_uri):
    """
    Generate the WorkOS authorization URL for Google OAuth
    """
    authorization_url = workos.client.sso.get_authorization_url(
        provider=sso.SsoProviderType.GoogleOAuth,
        redirect_uri=redirect_uri
    )
    return authorization_url


def get_profile_from_code(code):
    """
    Exchange authorization code for user profile
    """
    profile = workos.client.sso.get_profile_and_token(code)
    return profile

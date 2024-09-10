from .models import CustomUser
from google.auth.transport import requests
from google.oauth2 import id_token
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings

class Google_signin():
    """
    Class for Google Sign-In authentication.
    """
    @staticmethod
    def validate(acess_token):
        """
        Validate Google access token.

        The access token received from Google.

        Returns User data if validation is successful, otherwise None.
        """
        try:
            id_info=id_token.verify_oauth2_token(acess_token,requests.Request(),settings.GOOGLE_CLIENT_ID)
            if 'accounts.google.com' in id_info['iss']:
                return id_info
        except Exception as e:
            return None
        
def login_google_user(email):
    user = CustomUser.objects.filter(email=email).first()
    if not user:
        raise AuthenticationFailed("Invalid login credentials")
    user_tokens = user.tokens
    return user, user_tokens


def register_google_user(email):
    """
    Register a new user with Google credentials.

    Returns User information along with access and refresh tokens.
    """
    user = CustomUser.objects.filter(email=email)

    if user.exists():
        return login_google_user(email)
    else:
        password =  settings.CUSTOM_PASSWORD_FOR_AUTH
        register_mode='google'
        register_user = CustomUser.objects.create_user(email, password, register_mode=register_mode)
        register_user.save()
        return login_google_user(email)
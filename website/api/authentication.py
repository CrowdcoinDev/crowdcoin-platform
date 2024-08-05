__author__ = 'droog'
from tastypie.authentication import BasicAuthentication
from django.contrib.auth.models import User
from tastypie.models import ApiKey
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.contrib.auth.models import AnonymousUser, User
from django.utils import timezone

from tastypie.authentication import Authentication

import oauth2_provider
from oauth2_provider.models import AccessToken

import logging
logger = logging.getLogger(__name__)


class SessionAuthentication (BasicAuthentication):
    def __init__(self, *args, **kwargs):
        super(SessionAuthentication , self).__init__(*args, **kwargs)
 
    def is_authenticated(self, request, **kwargs):
        from django.contrib.sessions.models import Session
        if 'sessionid' in request.COOKIES:
            s = Session.objects.get(pk=request.COOKIES['sessionid'])
            if '_auth_user_id' in s.get_decoded():
                u = User.objects.get(id=s.get_decoded()['_auth_user_id'])
                request.user = u
                return True
        return super(SessionAuthentication , self).is_authenticated(request, **kwargs)

class TokenAuthentication (BasicAuthentication):
    def __init__(self, *args, **kwargs):
        super(TokenAuthentication, self).__init__(*args, **kwargs)

    def is_authenticated(self, request, **kwargs):
        token = request.GET.get('token')
        if ApiKey.objects.filter(key=token).exists():
            request.user = ApiKey.objects.get(key=token).user
            return True
        else:
            return super(TokenAuthentication, self).is_authenticated(request, **kwargs)


class InlineBasicAuthentication (BasicAuthentication):
    def __init__(self, *args, **kwargs):
        super(InlineBasicAuthentication, self).__init__(*args, **kwargs)

    def is_authenticated(self, request, **kwargs):
        username = request.GET.get('username')
        password = request.GET.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.user = user
            return True
        else:
            return super(InlineBasicAuthentication, self).is_authenticated(request, **kwargs)            



# stolen from piston
class OAuthError(RuntimeError):
    """Generic exception class."""
    def __init__(self, message='OAuth error occured.'):
        self.message = message


class OAuth20Authentication(Authentication):
    """
    OAuth authenticator. 

    This Authentication method checks for a provided HTTP_AUTHORIZATION
    and looks up to see if this is a valid OAuth Access Token
    """
    def __init__(self, realm='API'):
        self.realm = realm

    def is_authenticated(self, request, **kwargs):
        """
        Verify 2-legged oauth request. Parameters accepted as
        values in "Authorization" header, or as a GET request
        or in a POST body.
        """
        logging.info("OAuth20Authentication")

        try:
            key = request.GET.get('oauth_consumer_key')
            if not key:
                key = request.POST.get('oauth_consumer_key')
            if not key:
                auth_header_value = request.META.get('HTTP_AUTHORIZATION')
                if auth_header_value:
                    key = auth_header_value.split(' ')[1]
            if not key:
                logging.error('OAuth20Authentication. No consumer_key found.')
                return None
            """
            If verify_access_token() does not pass, it will raise an error
            """
            token = verify_access_token(key)

            # If OAuth authentication is successful, set the request user to the token user for authorization
            request.user = token.user

            # If OAuth authentication is successful, set oauth_consumer_key on request in case we need it later
            request.META['oauth_consumer_key'] = key
            return True
        except KeyError as e:
            logging.exception("Error in OAuth20Authentication.")
            request.user = AnonymousUser()
            return False
        except Exception as e:
            logging.exception("Error in OAuth20Authentication.")
            return False
        return True

def verify_access_token(key):
    # Check if key is in AccessToken key
    try:
        token = AccessToken.objects.get(token=key)

        # Check if token has expired
        if token.expires < timezone.now():
            raise OAuthError('AccessToken has expired.')
    except AccessToken.DoesNotExist as e:
        raise OAuthError("AccessToken not found at all.")

    logging.info('Valid access')
    return token            
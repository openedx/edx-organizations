"""Temp auth class to see how often oauth2authentication class is used in organizations"""
from rest_framework_oauth.authentication import OAuth2Authentication
from edx_django_utils.monitoring import set_custom_metric


class OAuth2AuthenticationDeprecated(OAuth2Authentication):
    """
    This child class was added to add new_relic metrics to OAuth2Authentication. This should be very temporary.
    """

    def authenticate(self, request):
        """
        Returns two-tuple of (user, token) if access token authentication
        succeeds, None if the user did not try to authenticate using an access
        token, or raises an AuthenticationFailed (HTTP 401) if authentication
        fails.
        """
        set_custom_metric("OAuth2AuthenticationDeprecated", "Failed")
        output = super(OAuth2AuthenticationDeprecated, self).authenticate(request)
        if output is None:
            set_custom_metric("OAuth2AuthenticationDeprecated", "None")
        else:
            set_custom_metric("OAuth2AuthenticationDeprecated", "Success")
        return output

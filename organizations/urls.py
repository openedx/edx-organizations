"""
URLS for organizations
"""
from django.conf.urls import url, include

# pylint: disable=invalid-name
urlpatterns = [
    url(r'^v0/', include('organizations.v0.urls', namespace='v0')),
]

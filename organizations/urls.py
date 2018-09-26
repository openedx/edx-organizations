"""
URLS for organizations
"""
from django.conf.urls import url, include

app_name = 'organizations'  # pylint: disable=invalid-name
urlpatterns = [
    url(r'^v0/', include('organizations.v0.urls')),
]

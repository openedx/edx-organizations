"""
URLS for organizations
"""
from django.conf.urls import re_path, include

app_name = 'organizations'  # pylint: disable=invalid-name
urlpatterns = [
    re_path(r'^v0/', include('organizations.v0.urls')),
]

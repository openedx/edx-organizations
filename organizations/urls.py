"""
URLS for organizations
"""
from django.urls import include, re_path

app_name = 'organizations'  # pylint: disable=invalid-name
urlpatterns = [
    re_path(r'^v0/', include('organizations.v0.urls')),
]

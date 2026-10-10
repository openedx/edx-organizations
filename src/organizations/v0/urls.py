"""
URLS for organizations end points.
"""
# pylint: disable=invalid-name
from rest_framework import routers

from organizations.v0.views import OrganizationsViewSet

router = routers.SimpleRouter()
router.register(r'organizations', OrganizationsViewSet)

app_name = 'v0'
urlpatterns = router.urls

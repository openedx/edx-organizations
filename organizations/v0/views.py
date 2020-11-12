"""
Views for organizations end points.
"""
from django.http import Http404
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from organizations.models import Organization
from organizations.permissions import UserIsStaff
from organizations.serializers import OrganizationSerializer


class OrganizationsViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    Organization view to:
        - fetch list organization data or single organization using organization short name.
        - create or update an organization via the PUT endpoint.
    """
    queryset = Organization.objects.filter(active=True)
    serializer_class = OrganizationSerializer
    lookup_field = 'short_name'
    authentication_classes = (JwtAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, UserIsStaff)

    def update(self, request, *args, **kwargs):
        """ We perform both Update and Create action via the PUT method. """
        try:
            return super(OrganizationsViewSet, self).update(request, *args, **kwargs)
        except Http404:
            serializer = OrganizationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """ We disable PATCH because all updates and creates should use the PUT action above. """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

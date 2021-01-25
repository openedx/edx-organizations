"""
Views for organizations end points.
"""
from django.http import Http404
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from organizations.models import Organization
from organizations.permissions import UserIsStaff
from organizations.serializers import OrganizationSerializer


class OrganizationsViewSet(mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    Organization view to:
        - list organization data (GET .../)
        - retrieve single organization (GET .../<short_name>)
        - create or update an organization via the PUT endpoint (PUT .../<short_name>)
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = 'short_name'
    authentication_classes = (JwtAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated, UserIsStaff)

    def get_queryset(self):
        """
        Get the queryset to use in the request.

        For listing and retieving organizations, we only want to include
        active ones.

        For creating and updating organizations, we want to include all of
        them, which allows API users to "create" (i.e., reactivate)
        organizations that exist internally but are inactive.
        """
        if self.request.method == "GET":
            return self.queryset.filter(active=True)
        return self.queryset

    def update(self, request, *args, **kwargs):
        """
        We perform both Update and Create action via the PUT method.

        The 'active' field may not be specified via the HTTP API, since it
        is always assumed to be True. So:
            (1) new organizations created through the API are always Active, and
            (2) existing organizations updated through the API always end up Active,
                regardless of whether or not they were previously active.
        """
        if 'active' in self.request.data:
            raise ValidationError(
                "Value of 'active' may not be specified via Organizations HTTP API."
            )
        self.request.data['active'] = True
        try:
            return super().update(request, *args, **kwargs)
        except Http404:
            serializer = OrganizationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """
        We disable PATCH because all updates and creates should use the PUT action above.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

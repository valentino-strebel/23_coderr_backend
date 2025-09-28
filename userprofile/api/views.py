"""
@file views.py
@description
    API endpoints for retrieving, updating, and listing user profiles.
"""

from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, parsers

from userprofile.models import Profile
from .serializers import (
    ProfileSerializer,
    BusinessProfileListSerializer,
    CustomerProfileListSerializer,
)
from core.permissions import IsAuthenticatedOnly, IsProfileOwnerOrReadOnly


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    @endpoint ProfileRetrieveUpdateView
    @routes
        GET   /api/profile/{pk}/
        PATCH /api/profile/{pk}/
    @auth
        GET   - Authenticated users.
        PATCH - Only the profile owner (403 otherwise).
    @notes
        {pk} is the *User* ID. The object lookup is performed via Profile.user_id == {pk}.
        The serializer ensures certain text fields are never null in responses.
    @editable_fields
        first_name, last_name, file, location, tel, description, working_hours, email
    """
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    # Make intent explicit: require auth for all, owner for writes
    permission_classes = [IsAuthenticatedOnly, IsProfileOwnerOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    lookup_field = "pk"

    def get_object(self):
        # {pk} refers to the User's ID, not the Profile's PK
        return get_object_or_404(self.get_queryset(), user_id=self.kwargs["pk"])


class BusinessProfileListView(generics.ListAPIView):
    """
    @endpoint BusinessProfileListView
    @route GET /api/profiles/business/
    @auth Authenticated users.
    @description
        Returns a list of all profiles with type "business".
        Response normalizes specific text fields to empty strings instead of null.
    """
    permission_classes = [IsAuthenticatedOnly]
    serializer_class = BusinessProfileListSerializer

    def get_queryset(self):
        return Profile.objects.select_related("user").filter(type="business")


class CustomerProfileListView(generics.ListAPIView):
    """
    @endpoint CustomerProfileListView
    @route GET /api/profiles/customer/
    @auth Authenticated users.
    @description
        Returns a list of all profiles with type "customer".
        Response normalizes specific text fields to empty strings instead of null.
    """
    permission_classes = [IsAuthenticatedOnly]
    serializer_class = CustomerProfileListSerializer

    def get_queryset(self):
        return Profile.objects.select_related("user").filter(type="customer")

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

from .permissions import IsProfileOwnerOrReadOnly


class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    """
    @endpoint ProfileRetrieveUpdateView
    @route GET /api/profile/{id}/
    @route PATCH /api/profile/{id}/
    @auth
        GET   - Authenticated users
        PATCH - Only the profile owner
    @description
        - GET: Returns the full profile (ensures nullable text fields return empty strings).
        - PATCH: Allows profile owners to update editable fields.
    @editable_fields
        first_name, last_name, file, location, tel, description, working_hours, email
    """
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    permission_classes = [IsProfileOwnerOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    lookup_field = "pk"

    # ✅ Important: your API spec says {pk} is the *User* id, not the Profile id.
    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            user_id=self.kwargs["pk"],
        )


class BusinessProfileListView(generics.ListAPIView):
    """
    @endpoint BusinessProfileListView
    @route GET /api/profiles/business/
    @auth Authenticated users
    @description
        Returns a list of all profiles with type "business".
        Ensures nullable text fields are represented as empty strings in the response.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessProfileListSerializer

    def get_queryset(self):
        return Profile.objects.select_related("user").filter(type="business")


class CustomerProfileListView(generics.ListAPIView):
    """
    @endpoint CustomerProfileListView
    @route GET /api/profiles/customer/
    @auth Authenticated users
    @description
        Returns a list of all profiles with type "customer".
        Ensures nullable text fields are represented as empty strings in the response.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerProfileListSerializer

    def get_queryset(self):
        return Profile.objects.select_related("user").filter(type="customer")

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
    GET /api/profile/{pk}/
      - Auth required
      - Returns full profile info (with empty strings for specified nullables)

    PATCH /api/profile/{pk}/
      - Auth required
      - ONLY the owner can update their own profile
      - Editable: first_name, last_name, file, location, tel, description, working_hours, email
    """
    queryset = Profile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    permission_classes = [IsProfileOwnerOrReadOnly]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    lookup_field = "pk"


class BusinessProfileListView(generics.ListAPIView):
    """
    GET /api/profiles/business/
      - Auth required
      - Returns a list of all 'business' profiles
      - Ensures specified text fields are never null in the response
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessProfileListSerializer

    def get_queryset(self):
        return Profile.objects.select_related("user").filter(type="business")


class CustomerProfileListView(generics.ListAPIView):
    """
    GET /api/profiles/customer/
      - Auth required
      - Returns a list of all 'customer' profiles
      - Ensures specified text fields are never null in the response
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CustomerProfileListSerializer

    def get_queryset(self):
        return Profile.objects.select_related("user").filter(type="customer")

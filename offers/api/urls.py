from django.urls import path
from .views import (
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
    OfferDetailRetrieveView,
)

urlpatterns = [
    # List (public) + Create (business users)
    path("api/offers/", OfferListCreateView.as_view(), name="offer-list-create"),

    # Retrieve (auth), Patch (owner), Delete (owner -> 204 No Content)
    path("api/offers/<int:pk>/", OfferRetrieveUpdateDestroyView.as_view(), name="offer-detail"),

    # Offer detail retrieve (auth)
    path("api/offerdetails/<int:pk>/", OfferDetailRetrieveView.as_view(), name="offerdetail-detail"),
]

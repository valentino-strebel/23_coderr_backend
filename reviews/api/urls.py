from django.urls import path
from .views import ReviewListCreateView, ReviewUpdateDestroyView

urlpatterns = [
    path("reviews/", ReviewListCreateView.as_view(), name="review-list-create"),
    path("reviews/<int:pk>/", ReviewUpdateDestroyView.as_view(), name="review-update-destroy"),
]

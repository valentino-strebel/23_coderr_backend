from django.urls import path
from .views import RegistrationView, LoginView

urlpatterns = [
    path("login/", RegistrationView.as_view(), name="login"),
    path("registration/", LoginView.as_view(), name="registration"),
]

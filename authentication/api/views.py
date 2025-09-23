from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.authtoken.models import Token

from .serializers import RegistrationSerializer, LoginSerializer


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            with transaction.atomic():
                user = serializer.save()
        except IntegrityError:
            return Response({"detail": "Benutzername oder E-Mail existiert bereits."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Interner Serverfehler."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.pk,
                "type": user.type,
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data["username"]
        password = serializer.validated_data["password"]

        try:
            user = authenticate(request=request, username=username, password=password)
        except Exception:
            return Response({"detail": "Interner Serverfehler."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if user is None:
            # Keep it generic to avoid leaking whether the username exists
            return Response({"detail": "Ungültige Anmeldedaten."}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        data = {
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.pk,
        }
        return Response(data, status=status.HTTP_200_OK)

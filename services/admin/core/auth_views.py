from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class CsrfView(APIView):
    def get(self, request):
        return Response({"csrfToken": get_token(request)})


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "")
        if not username or not password:
            return Response(
                {"detail": "username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(password) < 8:
            return Response(
                {"detail": "Password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if User.objects.filter(username=username).exists():
            return Response(
                {"detail": "Username already taken."},
                status=status.HTTP_409_CONFLICT,
            )
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        get_token(request)  # ensures csrftoken cookie is set
        return Response(
            {"id": user.id, "username": user.username},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username", "")
        password = request.data.get("password", "")
        if not username or not password:
            return Response(
                {"detail": "username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)
        get_token(request)  # ensures csrftoken cookie is set
        return Response({"id": user.id, "username": user.username})


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"id": request.user.id, "username": request.user.username})

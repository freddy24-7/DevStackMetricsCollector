from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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

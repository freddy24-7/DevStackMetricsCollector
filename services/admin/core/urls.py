from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include

from .auth_views import LoginView, LogoutView, MeView


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    path("api/admin/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/admin/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/admin/auth/me/", MeView.as_view(), name="auth-me"),
    path("api/admin/keys/", include("api_keys.urls")),
    path("api/admin/nodes/", include("nodes.urls")),
]

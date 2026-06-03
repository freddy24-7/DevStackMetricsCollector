from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health),
    path("admin/", admin.site.urls),
    path("api/admin/keys/", include("api_keys.urls")),
    path("api/admin/nodes/", include("nodes.urls")),
]

from django.urls import path
from . import views

urlpatterns = [
    path("", views.ApiKeyListCreateView.as_view(), name="apikey-list-create"),
    path("<uuid:pk>/revoke/", views.ApiKeyRevokeView.as_view(), name="apikey-revoke"),
]

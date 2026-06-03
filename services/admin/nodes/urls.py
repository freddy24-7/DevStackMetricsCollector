from django.urls import path
from . import views

urlpatterns = [
    path("", views.NodeListCreateView.as_view(), name="node-list-create"),
    path("<uuid:pk>/", views.NodeDetailView.as_view(), name="node-detail"),
]

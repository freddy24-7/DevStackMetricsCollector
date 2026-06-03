from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Node


class NodeListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        nodes = Node.objects.filter(user=request.user).values(
            "id", "hostname", "label", "created_at"
        )
        return Response(list(nodes))

    def post(self, request):
        hostname = request.data.get("hostname", "").strip()
        label = request.data.get("label", "").strip()
        if not hostname or not label:
            return Response(
                {"detail": "hostname and label are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        node = Node.objects.create(user=request.user, hostname=hostname, label=label)
        return Response(
            {"id": node.id, "hostname": node.hostname, "label": node.label, "created_at": node.created_at},
            status=status.HTTP_201_CREATED,
        )


class NodeDetailView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            node = Node.objects.get(pk=pk, user=request.user)
        except Node.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

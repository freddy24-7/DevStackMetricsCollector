from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ApiKey


class ApiKeyListCreateView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        keys = ApiKey.objects.filter(user=request.user).values(
            "id", "created_at", "revoked_at"
        )
        return Response(list(keys))

    def post(self, request):
        instance, raw_key = ApiKey.generate(request.user)
        return Response(
            {"id": instance.id, "key": raw_key, "created_at": instance.created_at},
            status=status.HTTP_201_CREATED,
        )


class ApiKeyRevokeView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            key = ApiKey.objects.get(pk=pk, user=request.user, revoked_at__isnull=True)
        except ApiKey.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        key.revoked_at = timezone.now()
        key.save(update_fields=["revoked_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

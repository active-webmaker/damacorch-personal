from rest_framework.response import Response
from rest_framework.views import APIView

from core.services import get_current_local_user
from sns_integration.models import SnsChannel, UserSnsAccount
from sns_integration.serializers import SnsChannelSerializer, UserSnsAccountSerializer


class SnsChannelsView(APIView):
    def get(self, request):
        qs = SnsChannel.objects.filter(is_active=True).order_by("id")
        return Response(SnsChannelSerializer(qs, many=True).data)


class MeSnsAccountsView(APIView):
    def get(self, request):
        user = get_current_local_user(request)
        qs = UserSnsAccount.objects.filter(user=user).select_related("sns_channel").order_by("id")
        return Response(UserSnsAccountSerializer(qs, many=True).data)


class SnsImportView(APIView):
    def post(self, request):
        # PoC placeholder: return an auth url.
        code = request.data.get("snsChannelCode")
        if not code:
            return Response({"detail": "snsChannelCode is required"}, status=400)
        return Response({"authUrl": f"https://example.com/oauth/{code}"})

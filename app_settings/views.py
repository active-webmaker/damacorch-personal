from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app_settings.models import AppSetting


class AppSettingsPublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        logo = AppSetting.objects.filter(key="service_logo_url").first()
        name = AppSetting.objects.filter(key="service_name").first()
        return Response(
            {
                "serviceLogoUrl": logo.value if logo else "",
                "serviceName": name.value if name else "",
            }
        )

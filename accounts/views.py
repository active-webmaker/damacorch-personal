from django.utils import timezone
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import (
    LoginRequestSerializer,
    SignupRequestSerializer,
    UserSummarySerializer,
)

from core.services import get_current_local_user


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        sub = f"dummy-{data['email']}"

        user, _created = User.objects.update_or_create(
            cognito_sub=sub,
            defaults={
                "email": data["email"],
                "name": data["name"],
                "age": data["age"],
                "gender": data["gender"],
            },
        )

        return Response(
            {
                "user": UserSummarySerializer(user).data,
                "accessToken": sub,
                "refreshToken": sub,
            }
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        sub = f"dummy-{data['email']}"

        user, _created = User.objects.update_or_create(
            cognito_sub=sub,
            defaults={
                "email": data["email"],
            },
        )
        user.last_login_at = timezone.now()
        user.save(update_fields=["last_login_at", "updated_at"])

        return Response(
            {
                "user": UserSummarySerializer(user).data,
                "accessToken": sub,
                "refreshToken": sub,
            }
        )


class LogoutView(APIView):
    def post(self, request):
        return Response({"success": True})


class MeView(APIView):
    def get(self, request):
        user = get_current_local_user(request)
        return Response(UserSummarySerializer(user).data)

from django.db.models import QuerySet
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import UserSummarySerializer
from analysis.models import AnalysisResult
from analysis.serializers import (
    AnalysisResultCreateRequestSerializer,
    AnalysisResultDetailSerializer,
    AnalysisResultListItemSerializer,
)
from core.services import get_current_local_user


class AnalysisResultDetailView(APIView):
    def get(self, request, id: int):
        obj = AnalysisResult.objects.filter(id=id).first()
        if obj is None:
            return Response({"detail": "Not found"}, status=404)
        return Response(AnalysisResultDetailSerializer(obj).data)


class AnalysisResultCreateView(APIView):
    def post(self, request):
        serializer = AnalysisResultCreateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User.objects.filter(id=data["userId"]).first()
        if user is None:
            return Response({"detail": "User not found"}, status=404)

        obj = AnalysisResult.objects.create(
            user=user,
            character_name=data["characterName"],
            character_image_url=data.get("characterImageUrl", ""),
            summary=data.get("summary", ""),
            tendency_personality=data.get("tendencyPersonality", ""),
            tendency_behavior_pattern=data.get("tendencyBehaviorPattern", ""),
            preference_likes=data.get("preferenceLikes", ""),
            preference_dislikes=data.get("preferenceDislikes", ""),
            coaching_tips=data.get("coachingTips", ""),
        )

        return Response({"id": obj.id, "createdAt": obj.created_at})


class UserAnalysisResultsView(APIView):
    def get(self, request, userId: int):
        qs: QuerySet[AnalysisResult] = AnalysisResult.objects.filter(user_id=userId).order_by("-created_at")

        page = int(request.query_params.get("page", "1") or 1)
        page_size = int(request.query_params.get("pageSize", "20") or 20)
        page = max(page, 1)
        page_size = max(min(page_size, 100), 1)
        offset = (page - 1) * page_size

        total_count = qs.count()
        items = qs[offset : offset + page_size]
        return Response(
            {
                "items": AnalysisResultListItemSerializer(items, many=True).data,
                "totalCount": total_count,
            }
        )


class MypageView(APIView):
    def get(self, request):
        user = get_current_local_user(request)
        recent = AnalysisResult.objects.filter(user=user).order_by("-created_at")[:5]
        return Response(
            {
                "user": UserSummarySerializer(user).data,
                "recentAnalysisResults": AnalysisResultListItemSerializer(recent, many=True).data,
            }
        )

from datetime import date, timedelta

from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.models import AnalysisResult
from core.services import get_current_local_user
from quests.models import QuestTemplate, UserQuest
from quests.serializers import (
    QuestBulkStatusRequestSerializer,
    QuestStatusUpdateRequestSerializer,
)


class HomeView(APIView):
    def get(self, request):
        user = get_current_local_user(request)
        today = timezone.localdate()
        week_start = today - timedelta(days=today.weekday())

        latest_result = (
            AnalysisResult.objects.filter(user=user).order_by("-created_at").first()
        )
        character = {
            "name": latest_result.character_name if latest_result else "",
            "imageUrl": latest_result.character_image_url if latest_result else "",
            "status": latest_result.summary if latest_result else "",
        }

        daily_qs = (
            UserQuest.objects.filter(user=user, period_date=today)
            .exclude(status="deleted")
            .select_related("quest_template")
            .filter(quest_template__type="daily")
            .order_by("id")[:3]
        )
        weekly_obj = (
            UserQuest.objects.filter(user=user, week_start_date=week_start)
            .exclude(status="deleted")
            .select_related("quest_template")
            .filter(quest_template__type="weekly")
            .order_by("id")
            .first()
        )

        def to_item(uq: UserQuest):
            return {
                "userQuestId": uq.id,
                "title": uq.quest_template.title,
                "description": uq.quest_template.description,
                "status": uq.status,
            }

        return Response(
            {
                "user": {"id": user.id, "email": user.email, "name": user.name},
                "character": character,
                "dailyQuests": [to_item(q) for q in daily_qs],
                "weeklyQuest": to_item(weekly_obj) if weekly_obj else None,
            }
        )


class QuestsView(APIView):
    def get(self, request):
        user = get_current_local_user(request)
        date_str = request.query_params.get("date")
        if date_str:
            base_date = date.fromisoformat(date_str)
        else:
            base_date = timezone.localdate()
        week_start = base_date - timedelta(days=base_date.weekday())

        qs = UserQuest.objects.filter(user=user).exclude(status="deleted").select_related("quest_template")
        daily = qs.filter(period_date=base_date, quest_template__type="daily").order_by("id")
        weekly = qs.filter(week_start_date=week_start, quest_template__type="weekly").order_by("id")

        def to_item(uq: UserQuest):
            return {
                "userQuestId": uq.id,
                "title": uq.quest_template.title,
                "description": uq.quest_template.description,
                "status": uq.status,
            }

        return Response(
            {
                "daily": [to_item(q) for q in daily],
                "weekly": [to_item(q) for q in weekly],
            }
        )


class QuestStatusView(APIView):
    def patch(self, request, userQuestId: int):
        user = get_current_local_user(request)
        obj = UserQuest.objects.filter(id=userQuestId, user=user).first()
        if obj is None:
            return Response({"detail": "Not found"}, status=404)

        serializer = QuestStatusUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        status_value = serializer.validated_data["status"]
        obj.status = status_value
        if status_value == "completed":
            obj.completed_at = timezone.now()
        obj.save(update_fields=["status", "completed_at"])
        return Response({"userQuestId": obj.id, "status": obj.status})


class QuestBulkStatusView(APIView):
    def patch(self, request):
        user = get_current_local_user(request)
        serializer = QuestBulkStatusRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data["userQuestIds"]
        status_value = serializer.validated_data["status"]
        qs = UserQuest.objects.filter(user=user, id__in=ids)
        updated = 0
        now = timezone.now()
        for obj in qs:
            obj.status = status_value
            if status_value == "completed":
                obj.completed_at = now
            obj.save(update_fields=["status", "completed_at"])
            updated += 1
        return Response({"updatedCount": updated})


class QuestHistoryByDateView(APIView):
    def get(self, request):
        user = get_current_local_user(request)
        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"detail": "date is required"}, status=400)
        target = date.fromisoformat(date_str)
        week_start = target - timedelta(days=target.weekday())

        qs = UserQuest.objects.filter(user=user).exclude(status="deleted").select_related("quest_template")
        daily = qs.filter(period_date=target, quest_template__type="daily")
        weekly = qs.filter(week_start_date=week_start, quest_template__type="weekly")

        def to_daily(uq: UserQuest):
            return {
                "userQuestId": uq.id,
                "title": uq.quest_template.title,
                "description": uq.quest_template.description,
                "status": uq.status,
                "completedAt": uq.completed_at,
            }

        def to_weekly(uq: UserQuest):
            return {
                "userQuestId": uq.id,
                "title": uq.quest_template.title,
                "description": uq.quest_template.description,
                "status": uq.status,
                "weekStartDate": str(uq.week_start_date) if uq.week_start_date else None,
            }

        return Response(
            {
                "date": date_str,
                "dailyQuests": [to_daily(q) for q in daily],
                "weeklyQuests": [to_weekly(q) for q in weekly],
            }
        )


class QuestHistorySummaryView(APIView):
    def get(self, request):
        user = get_current_local_user(request)
        year = request.query_params.get("year")
        month = request.query_params.get("month")
        if not year or not month:
            return Response({"detail": "year and month are required"}, status=400)
        year_i = int(year)
        month_i = int(month)
        first = date(year_i, month_i, 1)
        if month_i == 12:
            next_month = date(year_i + 1, 1, 1)
        else:
            next_month = date(year_i, month_i + 1, 1)

        qs = UserQuest.objects.filter(user=user).exclude(status="deleted").select_related("quest_template")
        # daily quests within month
        daily = qs.filter(period_date__gte=first, period_date__lt=next_month, quest_template__type="daily")
        by_day = (
            daily.values("period_date")
            .annotate(total=Count("id"), completed=Count("id", filter=Q(status="completed")))
            .order_by("period_date")
        )

        days = []
        for row in by_day:
            d = row["period_date"]
            days.append(
                {
                    "date": d.isoformat(),
                    "hasQuest": row["total"] > 0,
                    "completedCount": row["completed"],
                    "totalCount": row["total"],
                }
            )

        return Response({"year": year_i, "month": month_i, "days": days})

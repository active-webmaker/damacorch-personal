from rest_framework.response import Response
from rest_framework.views import APIView

from core.services import get_current_local_user
from selfcheck.models import SelfCheckEntry
from selfcheck.serializers import (
    SelfCheckEntryResponseSerializer,
    SelfCheckSubmitRequestSerializer,
)


class SelfCheckInitView(APIView):
    def get(self, request):
        user = get_current_local_user(request)
        last = SelfCheckEntry.objects.filter(user=user).order_by("-created_at").first()
        return Response(
            {
                "user": {"id": user.id, "name": user.name, "age": user.age, "gender": user.gender},
                "lastSelfCheck": SelfCheckEntryResponseSerializer(last).data if last else None,
            }
        )


class SelfCheckSubmitView(APIView):
    def post(self, request):
        user = get_current_local_user(request)
        serializer = SelfCheckSubmitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        entry = SelfCheckEntry.objects.create(
            user=user,
            hobby=data.get("hobby", ""),
            sleep_pattern=data.get("sleepPattern", ""),
            exercise_flag=data.get("exerciseFlag", False),
            exercise_per_week=data.get("exercisePerWeek"),
            exercise_type=data.get("exerciseType", ""),
            pet_type=data.get("petType", ""),
            mbti=data.get("mbti", ""),
            outing_per_week=data.get("outingPerWeek"),
            speech_audio_path=data.get("speechAudioPath"),
            self_intro_doc_path=data.get("selfIntroDocPath"),
        )

        return Response({"selfCheckId": entry.id, "message": "셀프 체크 정보가 저장되었습니다."})

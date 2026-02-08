import random

from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from analysis.models import AnalysisResult, EgogramType
from core.services import get_current_local_user
from psy.models import PsyAnswer, PsyQuestion, PsyTestSession
from psy.serializers import PsyQuestionSerializer, PsySubmitRequestSerializer


class PsyQuestionsView(APIView):
    def get(self, request):
        qs = PsyQuestion.objects.all().order_by("order_index")
        return Response(PsyQuestionSerializer(qs, many=True).data)


class PsySubmitView(APIView):
    def post(self, request):
        user = get_current_local_user(request)
        serializer = PsySubmitRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        session = None
        session_id = data.get("sessionId")
        if session_id:
            session = PsyTestSession.objects.filter(id=session_id, user=user).first()
        if session is None:
            session = PsyTestSession.objects.create(user=user, status="completed", completed_at=timezone.now())

        answers = data.get("answers", [])
        for item in answers:
            q = PsyQuestion.objects.filter(id=item["questionId"]).first()
            if not q:
                continue
            PsyAnswer.objects.create(user=user, session=session, question=q, answer_value=item["value"])

        # PoC: pick a random egogram type as result, use its interpretation as summary.
        egos = list(EgogramType.objects.all()[:243])
        if egos:
            ego = random.choice(egos)
            character_name = ego.code
            summary = ego.interpretation
        else:
            character_name = ""
            summary = ""

        result = AnalysisResult.objects.create(
            user=user,
            character_name=character_name,
            character_image_url="",
            summary=summary,
            tendency_personality="",
            tendency_behavior_pattern="",
            preference_likes="",
            preference_dislikes="",
            coaching_tips="",
            source_type="psy_test",
            source_id=session.id,
        )

        return Response(
            {
                "analysisResultId": result.id,
                "redirectPath": f"/analysis-result?resultId={result.id}",
            }
        )

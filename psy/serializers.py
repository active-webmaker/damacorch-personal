from rest_framework import serializers

from psy.models import PsyAnswer, PsyQuestion


class PsyQuestionSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(source="order_index")
    text = serializers.CharField()
    scaleMin = serializers.IntegerField(source="scale_min")
    scaleMax = serializers.IntegerField(source="scale_max")

    class Meta:
        model = PsyQuestion
        fields = ["id", "order", "text", "scaleMin", "scaleMax"]


class PsyAnswerItemSerializer(serializers.Serializer):
    questionId = serializers.IntegerField()
    value = serializers.IntegerField()


class PsySubmitRequestSerializer(serializers.Serializer):
    sessionId = serializers.IntegerField(required=False, allow_null=True)
    answers = PsyAnswerItemSerializer(many=True)

from rest_framework import serializers

from selfcheck.models import SelfCheckEntry


class SelfCheckSubmitRequestSerializer(serializers.Serializer):
    hobby = serializers.CharField(required=False, allow_blank=True)
    sleepPattern = serializers.CharField(required=False, allow_blank=True)
    exerciseFlag = serializers.BooleanField(required=False)
    exercisePerWeek = serializers.IntegerField(required=False, allow_null=True)
    exerciseType = serializers.CharField(required=False, allow_blank=True)
    petType = serializers.CharField(required=False, allow_blank=True)
    mbti = serializers.CharField(required=False, allow_blank=True)
    outingPerWeek = serializers.IntegerField(required=False, allow_null=True)
    speechAudioPath = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    selfIntroDocPath = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class SelfCheckEntryResponseSerializer(serializers.ModelSerializer):
    sleepPattern = serializers.CharField(source="sleep_pattern")
    exerciseFlag = serializers.BooleanField(source="exercise_flag")
    exercisePerWeek = serializers.IntegerField(source="exercise_per_week")
    exerciseType = serializers.CharField(source="exercise_type")
    petType = serializers.CharField(source="pet_type")
    outingPerWeek = serializers.IntegerField(source="outing_per_week")
    speechAudioUrl = serializers.CharField(source="speech_audio_path")
    selfIntroDocUrl = serializers.CharField(source="self_intro_doc_path")

    class Meta:
        model = SelfCheckEntry
        fields = [
            "hobby",
            "sleepPattern",
            "exerciseFlag",
            "exercisePerWeek",
            "exerciseType",
            "petType",
            "mbti",
            "outingPerWeek",
            "speechAudioUrl",
            "selfIntroDocUrl",
        ]

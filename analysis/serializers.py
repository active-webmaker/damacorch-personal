from rest_framework import serializers

from analysis.models import AnalysisResult


class AnalysisResultListItemSerializer(serializers.ModelSerializer):
    characterName = serializers.CharField(source="character_name")
    createdAt = serializers.DateTimeField(source="created_at")

    class Meta:
        model = AnalysisResult
        fields = ["id", "characterName", "summary", "createdAt"]


class AnalysisResultDetailSerializer(serializers.ModelSerializer):
    userId = serializers.IntegerField(source="user_id")
    characterName = serializers.CharField(source="character_name")
    characterImageUrl = serializers.CharField(source="character_image_url")
    createdAt = serializers.DateTimeField(source="created_at")

    tendency = serializers.SerializerMethodField()
    preference = serializers.SerializerMethodField()
    coaching = serializers.SerializerMethodField()

    class Meta:
        model = AnalysisResult
        fields = [
            "id",
            "userId",
            "characterName",
            "characterImageUrl",
            "summary",
            "tendency",
            "preference",
            "coaching",
            "createdAt",
        ]

    def get_tendency(self, obj):
        return {"personality": obj.tendency_personality, "behaviorPattern": obj.tendency_behavior_pattern}

    def get_preference(self, obj):
        return {"likes": obj.preference_likes, "dislikes": obj.preference_dislikes}

    def get_coaching(self, obj):
        return {"tips": obj.coaching_tips}


class AnalysisResultCreateRequestSerializer(serializers.Serializer):
    userId = serializers.IntegerField()
    characterName = serializers.CharField()
    characterImageUrl = serializers.CharField(required=False, allow_blank=True)
    summary = serializers.CharField(required=False, allow_blank=True)
    tendencyPersonality = serializers.CharField(required=False, allow_blank=True)
    tendencyBehaviorPattern = serializers.CharField(required=False, allow_blank=True)
    preferenceLikes = serializers.CharField(required=False, allow_blank=True)
    preferenceDislikes = serializers.CharField(required=False, allow_blank=True)
    coachingTips = serializers.CharField(required=False, allow_blank=True)

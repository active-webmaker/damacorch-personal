from rest_framework import serializers

from quests.models import UserQuest


class QuestItemSerializer(serializers.Serializer):
    userQuestId = serializers.IntegerField()
    title = serializers.CharField()
    description = serializers.CharField()
    status = serializers.CharField()


class QuestStatusUpdateRequestSerializer(serializers.Serializer):
    status = serializers.CharField()


class QuestStatusUpdateResponseSerializer(serializers.Serializer):
    userQuestId = serializers.IntegerField()
    status = serializers.CharField()


class QuestBulkStatusRequestSerializer(serializers.Serializer):
    userQuestIds = serializers.ListField(child=serializers.IntegerField())
    status = serializers.CharField()

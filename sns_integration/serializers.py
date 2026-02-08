from rest_framework import serializers

from sns_integration.models import SnsChannel, UserSnsAccount


class SnsChannelSerializer(serializers.ModelSerializer):
    iconUrl = serializers.CharField(source="icon_url")

    class Meta:
        model = SnsChannel
        fields = ["id", "code", "name", "iconUrl"]


class UserSnsAccountSerializer(serializers.ModelSerializer):
    snsChannel = SnsChannelSerializer(source="sns_channel")

    class Meta:
        model = UserSnsAccount
        fields = ["snsChannel", "status", "display_name"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["displayName"] = data.pop("display_name")
        return data

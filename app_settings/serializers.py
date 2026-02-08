from rest_framework import serializers


class AppSettingsPublicResponseSerializer(serializers.Serializer):
    serviceLogoUrl = serializers.CharField(allow_blank=True)
    serviceName = serializers.CharField(allow_blank=True)

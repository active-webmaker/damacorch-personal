from rest_framework import serializers

from accounts.models import User


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name"]


class SignupRequestSerializer(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField()
    gender = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    passwordConfirm = serializers.CharField()

    def validate(self, attrs):
        if attrs.get("password") != attrs.get("passwordConfirm"):
            raise serializers.ValidationError({"passwordConfirm": "password mismatch"})
        return attrs


class LoginRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

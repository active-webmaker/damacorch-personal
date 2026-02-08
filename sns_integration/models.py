from django.db import models

from accounts.models import User


class SnsChannel(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    icon_url = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserSnsAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sns_accounts")
    sns_channel = models.ForeignKey(SnsChannel, on_delete=models.CASCADE)
    external_user_id = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    access_token = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="connected")
    connected_at = models.DateTimeField(auto_now_add=True)
    disconnected_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

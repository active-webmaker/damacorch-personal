from django.db import models

from accounts.models import User


class AnalysisResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="analysis_results")
    character_name = models.CharField(max_length=100)
    character_image_url = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    tendency_personality = models.TextField(blank=True)
    tendency_behavior_pattern = models.TextField(blank=True)
    preference_likes = models.TextField(blank=True)
    preference_dislikes = models.TextField(blank=True)
    coaching_tips = models.TextField(blank=True)
    source_type = models.CharField(max_length=50, null=True, blank=True)
    source_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EgogramType(models.Model):
    code = models.CharField(max_length=20, unique=True)
    interpretation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

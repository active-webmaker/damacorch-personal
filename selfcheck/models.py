from django.db import models

from accounts.models import User


class SelfCheckEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="self_check_entries")
    hobby = models.TextField(blank=True)
    sleep_pattern = models.CharField(max_length=50, blank=True)
    exercise_flag = models.BooleanField(default=False)
    exercise_per_week = models.IntegerField(null=True, blank=True)
    exercise_type = models.CharField(max_length=20, blank=True)
    pet_type = models.CharField(max_length=100, blank=True)
    mbti = models.CharField(max_length=4, blank=True)
    outing_per_week = models.IntegerField(null=True, blank=True)
    speech_audio_path = models.CharField(max_length=255, null=True, blank=True)
    self_intro_doc_path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

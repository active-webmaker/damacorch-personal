from django.db import models

from accounts.models import User


class QuestTemplate(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserQuest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_quests")
    quest_template = models.ForeignKey(QuestTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default="pending")
    period_date = models.DateField(null=True, blank=True)
    week_start_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

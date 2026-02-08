from django.db import models

from accounts.models import User


class PsyQuestion(models.Model):
    code = models.CharField(max_length=50, null=True, blank=True)
    text = models.TextField()
    order_index = models.IntegerField()
    scale_min = models.IntegerField(default=1)
    scale_max = models.IntegerField(default=5)
    reverse_scored = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PsyTestSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="psy_test_sessions")
    status = models.CharField(max_length=20, default="in_progress")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)


class PsyAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="psy_answers")
    session = models.ForeignKey(PsyTestSession, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.ForeignKey(PsyQuestion, on_delete=models.CASCADE)
    answer_value = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

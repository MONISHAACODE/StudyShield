from django.db import models
from django.conf import settings


class FocusSession(models.Model):
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
    focus_time = models.IntegerField()
    website = models.CharField(max_length=200)
    subject = models.CharField(max_length=100,default="General")
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    distraction_count = models.IntegerField(default=0)
    focus_score = models.IntegerField(default=100)
    session_rating = models.IntegerField(default=0)

    def __str__(self):
        return self.website


class StudyPlan(models.Model):
    user = models.ForeignKey('auth.User',on_delete=models.CASCADE,null=True,blank=True)
    subject = models.CharField(max_length=100)
    study_time = models.IntegerField()
    interest_level = models.IntegerField(default=3)
    mood = models.CharField(max_length=30, default="Good")
    plan_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Pending")

    def __str__(self):
        return self.subject

class ChallengeResult(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    category = models.CharField(max_length=50)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=5)
    correct_answers = models.IntegerField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.score}%"

    

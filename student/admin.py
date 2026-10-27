from django.contrib import admin
from .models import FocusSession, StudyPlan, ChallengeResult


@admin.register(ChallengeResult)
class ChallengeResultAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'category',
        'score',
        'total_questions',
        'correct_answers',
        'completed_at',
    )

    list_filter = ('category', 'completed_at')
    search_fields = ('user__username', 'category')
    ordering = ('-completed_at',)


@admin.register(FocusSession)
class FocusSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'website',
        'focus_time',
        'status',
        'distraction_count',
        'focus_score',
        'session_rating',
        'created_at',
    )

    list_filter = ('status', 'session_rating')
    search_fields = ('website',)
    ordering = ('-created_at',)


@admin.register(StudyPlan)
class StudyPlanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subject',
        'study_time',
        'plan_date',
        'status',
    )

    list_filter = ('status', 'plan_date')
    search_fields = ('subject',)
    ordering = ('-plan_date',)
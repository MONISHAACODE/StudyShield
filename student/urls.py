from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('study-planner/', views.study_planner, name='study_planner'),
    path('daily-checkin/', views.daily_checkin, name='daily_checkin'),
    path('interest-check/', views.interest_check, name='interest_check'),
    path('study-time/', views.study_time, name='study_time'),
    path('study-plan/', views.study_plan, name='study_plan'),
    path('start-planned-session/',views.start_planned_session,name='start_planned_session'),
    path('focus/', views.focus, name='focus'),
    path('sessions/', views.sessions, name='sessions'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("challenges/", views.challenges, name="challenges"),
    path("challenge-question/",views.challenge_question,name="challenge_question"),
    path("save-challenge-result/",views.save_challenge_result,name="save_challenge_result"),
    path('api/blocked-websites/', views.blocked_websites, name='blocked_websites'),
    path('stop-session/<int:session_id>/', views.stop_session, name='stop_session'),
    path('complete-session/<int:session_id>/', views.complete_session, name='complete_session'),
    path("save-session-rating/<int:session_id>/",views.save_session_rating,name="save_session_rating"),
    path('api/record-distraction/',views.record_distraction,name='record_distraction'),
    path("weekly-report/",views.weekly_focus_report,name="weekly_focus_report"),
    path("puzzle-zone/", views.puzzle_zone, name="puzzle_zone"),
]
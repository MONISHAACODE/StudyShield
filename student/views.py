from django.shortcuts import render, redirect
from .models import FocusSession, StudyPlan, ChallengeResult
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib import messages

def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "student/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "student/register.html")

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("/daily-checkin/")

    return render(request, "student/register.html")

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("/daily-checkin")

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    return render(
        request,
        "student/login.html"
    )

def user_logout(request):
    logout(request)
    return redirect("/login/")

def home(request):
    return render(request, 'student/home.html')

@login_required
def daily_checkin(request):
    if request.method == "POST":
        mood = request.POST.get("mood")

        request.session["daily_mood"] = mood

        return redirect("/study-planner/")

    return render(
        request,
        "student/daily_checkin.html"
    )

@login_required
def study_planner(request):

    if request.method == "POST":

        subjects = request.POST.getlist("subjects")

        # Empty subjects remove
        subjects = [
            subject.strip()
            for subject in subjects
            if subject.strip()
        ]

        # Save subjects temporarily for next step
        request.session["study_subjects"] = subjects
        request.session["study_plan_saved"] = False

        return redirect("/interest-check/")

    return render(
        request,
        "student/study_planner.html"
    )


@login_required
def interest_check(request):

    subjects = request.session.get("study_subjects", [])

    if not subjects:
        return redirect("/study-planner/")

    if request.method == "POST":

        study_interests = []

        for index, subject in enumerate(subjects, start=1):

            interest = request.POST.get(
                f"interest_{index}"
            )

            if not interest:
                return render(
                    request,
                    "student/interest_check.html",
                    {"subjects": subjects}
                )

            study_interests.append({
                "subject": subject,
                "interest": interest
            })

        request.session["study_interests"] = study_interests

        print("INTERESTS SAVED:", study_interests)

        return redirect("/study-time/")

    return render(
        request,
        "student/interest_check.html",
        {"subjects": subjects}
    )


@login_required
def study_time(request):

    study_interests = request.session.get("study_interests", [])

    if not study_interests:
        return redirect("/study-planner/")

    if request.method == "POST":

        available_time = request.POST.get("available_time")

        request.session["available_time"] = available_time

        return redirect("/study-plan/")

    return render(
        request,
        "student/study_time.html",
        {
            "study_interests": study_interests
        }
    )

@login_required
def study_plan(request):

    study_interests = request.session.get("study_interests", [])
    available_time = request.session.get("available_time")

    if not study_interests or not available_time:
        return redirect("/study-planner/")

    available_time = int(available_time)

    # Interest values
    interest_values = {
        "High": 5,
        "Medium": 3,
        "Low": 1
    }

    # Calculate total interest
    total_interest = sum(
        interest_values.get(item["interest"], 1)
        for item in study_interests
    )

    # Initial time allocation
    allocations = []

    for item in study_interests:

        weight = interest_values.get(
            item["interest"],
            1
        )

        minutes = (
            available_time * weight
        ) // total_interest

        allocations.append({
            "subject": item["subject"],
            "interest": item["interest"],
            "minutes": minutes
        })

    # Make sure total time is exactly equal
    allocated_total = sum(
        item["minutes"]
        for item in allocations
    )

    remaining = available_time - allocated_total

    
    index = 0

    while remaining > 0:
        allocations[index]["minutes"] += 1
        remaining -= 1
        index = (index + 1) % len(allocations)

    # Save each subject only once
    if not request.session.get("study_plan_saved", False):
        for item in allocations:
            StudyPlan.objects.create(
                user=request.user,
                subject=item["subject"],
                study_time=item["minutes"],
                interest_level=interest_values.get(
                    item["interest"], 1
                ),
                mood=request.session.get("daily_mood", "Good"),
                status="Pending"
            )

        request.session["study_plan_saved"] = True

    request.session["study_allocations"] = allocations
   

    return render(
        request,
        "student/study_plan.html",
        {
            "allocations": allocations,
            "available_time": available_time
        }
    )


@login_required
def start_planned_session(request):

    allocations = request.session.get("study_allocations", [])
    current_index = request.session.get("current_subject_index", 0)

    if not allocations:
        return redirect("/study-planner/")

    if current_index >= len(allocations):
        return redirect("/dashboard/")

    current_subject = allocations[current_index]

    return render(
        request,
        "student/focus.html",
        {
            "planned_subject": current_subject["subject"],
            "planned_time": current_subject["minutes"],
        }
    )

@login_required
def focus(request):
    message = ""
    selected_time = None
    session_id = None

    if request.method == 'POST':

        focus_time = request.POST.get('focus_time')
        website = request.POST.get('website')
        subject = request.POST.get('subject')

        active_session = FocusSession.objects.filter(
            user=request.user,
            status="Active"
        ).first()

        if active_session:
            message = "You already have an active focus session."

        else:
            session = FocusSession.objects.create(
                user=request.user,
                focus_time=focus_time,
                website=website,
                subject=subject
            )


            message = "Focus Session Started Successfully!"
            selected_time = focus_time
            session_id = session.id
    

    return render(
        request,
        'student/focus.html',
        {
            'message': message,
            'selected_time': selected_time,
            'session_id': session_id
        }
    )

@login_required
def dashboard(request):

    user_sessions = FocusSession.objects.filter(
    user=request.user
)

    total_sessions = user_sessions.count()

    active_sessions = user_sessions.filter(
        status='Active'
    ).count()

    completed_sessions = user_sessions.filter(
        status='Inactive'
    ).count()

    completed = user_sessions.filter(
        status='Inactive'
    )

    latest_challenge = ChallengeResult.objects.filter(
        user=request.user
        ).order_by('-completed_at').first()

    total_focus_minutes = sum(
        session.focus_time for session in completed
    )

    total_distractions = sum(
        session.distraction_count for session in completed
    )
    rated_sessions = completed.exclude(session_rating=0)

    if completed_sessions > 0:

        average_focus_score = round(
            sum(session.focus_score for session in completed)
            / completed_sessions
        )

        if rated_sessions.exists():
            average_rating = round(
                sum(session.session_rating for session in rated_sessions)
                / rated_sessions.count(),
                1
            )
        else:
            average_rating = 0

    else:
        average_focus_score = 0
        average_rating = 0
   
    quotes = [
            "Small steps every day create big results.",
            "Focus today, thank yourself tomorrow.",
            "Your future needs your focus, not your excuses.",
            "One focused hour can change your entire day.",
            "Progress matters more than perfection.",
            "Stay focused. Your goals are waiting.",
            "Discipline turns dreams into reality.",
            "Don't stop when it's difficult. Stop when it's done.",
            "Every focused minute takes you closer to your goal.",
            "Believe in your ability to learn.",

            "You don't need to be perfect. Just keep improving.",
            "Today's effort becomes tomorrow's confidence.",
            "Focus on what you can achieve today.",
            "Your hard work will speak for you.",
            "A little progress is still progress.",
            "Dream big, start small, stay consistent.",
            "Your goals deserve your attention.",
            "Make today better than yesterday.",
            "Success begins with showing up.",
            "Keep learning. Keep growing. Keep going.",

            "Don't let distractions decide your future.",
            "Your time is valuable. Spend it wisely.",
            "Focus is a superpower. Use it.",
            "One task. One goal. One step at a time.",
            "You are closer than you think.",
            "Consistency beats temporary motivation.",
            "Every session makes you stronger.",
            "Turn your screen time into study time.",
            "Your effort today builds your tomorrow.",
            "Stay patient. Great results take time.",

            "You can do hard things. Keep going.",
            "Don't compare your journey with someone else's.",
            "Your only competition is yesterday's you.",
            "Start before you feel ready.",
            "The best investment is in yourself.",
            "Keep your eyes on the goal, not the distraction.",
            "Your dreams need action, not just wishes.",
            "Focus now. Celebrate later.",
            "Every challenge is a chance to grow.",
            "Your determination is stronger than your distractions.",

            "Study with purpose, not pressure.",
            "A focused mind can achieve amazing things.",
            "Don't give up on the person you're becoming.",
            "Your future self will thank you for today's effort.",
            "One session at a time, one goal at a time.",
            "Make your focus stronger than your excuses.",
            "You started for a reason. Keep going.",
            "Your potential grows when you keep practicing.",
            "Today is another chance to improve.",
            "Stay focused today. Your dream is worth it."
            ]
                    

    quote_index = timezone.localdate().toordinal() % len(quotes)
    daily_quote = quotes[quote_index]




    # ================= FOCUS STREAK =================

    completed_dates = set(
        session.created_at.date()
        for session in completed
    )

    today = timezone.localdate()
    focus_streak = 0
    current_date = today

    while current_date in completed_dates:
        focus_streak += 1
        current_date -= timedelta(days=1)

   

    return render(
        request,
        'student/dashboard.html',
        {
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'completed_sessions': completed_sessions,
            'total_focus_minutes': total_focus_minutes,
            'total_distractions': total_distractions,
            'average_focus_score': average_focus_score,
            'average_rating': average_rating,
            'recent_sessions': completed.order_by('-created_at')[:5],
            'focus_streak': focus_streak,
            'daily_quote': daily_quote,
            'latest_challenge': latest_challenge,
        }
    )

@login_required
def sessions(request):

    all_sessions = FocusSession.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'student/sessions.html',
        {'sessions': all_sessions}
    )
@login_required
def blocked_websites(request):
    active_sessions = FocusSession.objects.filter(
        user=request.user,
        status="Active"
    )

    websites = []

    for session in active_sessions:
        for website in session.website.split(","):
            website = website.strip()
            if website:
                websites.append(website)

    return JsonResponse({
        "blocked_websites": websites
    })

@login_required
def stop_session(request, session_id):

    session = FocusSession.objects.get(
    id=session_id,
    user=request.user
)

    session.status = 'Inactive'
    session.save()

    current_index = request.session.get(
        "current_subject_index",
        0
    )

    request.session["current_subject_index"] = current_index + 1

    return redirect("/sessions/")
    
    
@login_required
def save_session_rating(request, session_id):

    if request.method == "POST":

        rating = int(request.POST.get("rating", 0))

        if 1 <= rating <= 5:

            session = FocusSession.objects.get(
                id=session_id,
                user=request.user
            )

            session.session_rating = rating
            session.save()

            return redirect("/sessions/")

    return redirect("/sessions/")


@login_required
def complete_session(request, session_id):
    from django.db import transaction
    from django.http import JsonResponse
    from django.shortcuts import get_object_or_404

    with transaction.atomic():
        session = get_object_or_404(
            FocusSession.objects.select_for_update(),
            id=session_id,
            user=request.user
        )

        if session.status == "Inactive":
            return JsonResponse({
                "success": True,
                "message": "Focus Session already completed"
            })

        session.status = "Inactive"
        session.save(update_fields=["status"])

        return JsonResponse({
            "success": True,
            "message": "Focus Session Completed",
            "celebration": True,
            "redirect_url": "/sessions/"
        })




@csrf_exempt
@login_required
def record_distraction(request):

    if request.method != "POST":
        return JsonResponse({
            "success": False,
            "message": "POST request required"
        }, status=405)

    website = request.POST.get("website", "").strip().lower()
    website = website.removeprefix("www.")

    if not website:
        return JsonResponse({
            "success": False,
            "message": "Website is required"
        }, status=400)

    session = FocusSession.objects.filter(
        user=request.user,
        status="Active"
    ).order_by("-created_at").first()

    if not session:
        return JsonResponse({
            "success": False,
            "message": "No active focus session found"
        }, status=404)

    blocked_websites = [
        site.strip().lower().removeprefix("www.")
        for site in session.website.split(",")
        if site.strip()
    ]

    if website in blocked_websites:

        session.distraction_count += 1

        # Example scoring rule: minus 10 per distraction
        session.focus_score = max(
            0,
            100 - (session.distraction_count * 10)
        )

        session.save(update_fields=[
            "distraction_count",
            "focus_score"
        ])

        return JsonResponse({
            "success": True,
            "distraction_count": session.distraction_count,
            "focus_score": session.focus_score
        })

    return JsonResponse({
        "success": False,
        "message": "Website does not match the active session"
    }, status=400)


def challenges(request):
    return render(request, "student/challenges.html")

def challenge_question(request):
    return render(request, "student/challenge_question.html")

@csrf_exempt
@login_required
def save_challenge_result(request):

    if request.method == "POST":

        category = request.POST.get("category")
        score = int(request.POST.get("score", 0))
        total_questions = int(request.POST.get("total_questions", 5))
        correct_answers = int(request.POST.get("correct_answers", 0))

        percentage = round(
            (score / total_questions) * 100
        )

        ChallengeResult.objects.create(
            user=request.user,
            category=category,
            score=percentage,
            total_questions=total_questions,
            correct_answers=correct_answers
        )

        return JsonResponse({
            "success": True,
            "message": "Challenge result saved successfully"
        })

    return JsonResponse({
        "success": False,
        "message": "POST request required"
    })


@login_required
def weekly_focus_report(request):
    today = timezone.localdate()
    start_date = today - timedelta(days=6)

    # Last 7 days completed sessions
    completed_sessions = FocusSession.objects.filter(
        user=request.user,
        status="Inactive",
        created_at__date__range=(start_date, today)
    )

    # Summary calculations
    total_sessions = completed_sessions.count()

    total_focus_minutes = sum(
        int(session.focus_time or 0)
        for session in completed_sessions
    )

    total_distractions = sum(
        session.distraction_count or 0
        for session in completed_sessions
    )

    average_focus_score = (
        round(sum(session.focus_score or 0 for session in completed_sessions)
              / total_sessions)
        if total_sessions else 0
    )

    rated_sessions = completed_sessions.exclude(session_rating=0)

    average_rating = (
        round(
            sum(session.session_rating for session in rated_sessions)
            / rated_sessions.count(),
            1
        )
        if rated_sessions.exists() else 0
    )

    # Prepare chart data for each of the last 7 days
    chart_labels = []
    chart_focus_minutes = []
    chart_focus_scores = []

    best_day = "No data"
    best_day_minutes = 0

    for day_offset in range(7):
        current_day = start_date + timedelta(days=day_offset)

        day_sessions = completed_sessions.filter(
            created_at__date=current_day
        )

        day_minutes = sum(
            int(session.focus_time or 0)
            for session in day_sessions
        )

        day_count = day_sessions.count()

        day_score = (
            round(
                sum(session.focus_score or 0 for session in day_sessions)
                / day_count
            )
            if day_count else 0
        )

        chart_labels.append(current_day.strftime("%a"))
        chart_focus_minutes.append(day_minutes)
        chart_focus_scores.append(day_score)

        if day_minutes > best_day_minutes:
            best_day_minutes = day_minutes
            best_day = current_day.strftime("%A")

    context = {
        "start_date": start_date,
        "end_date": today,
        "total_sessions": total_sessions,
        "total_focus_minutes": total_focus_minutes,
        "total_distractions": total_distractions,
        "average_focus_score": average_focus_score,
        "average_rating": average_rating,
        "best_day": best_day,
        "chart_labels": chart_labels,
        "chart_focus_minutes": chart_focus_minutes,
        "chart_focus_scores": chart_focus_scores,
    }

    return render(
        request,
        "student/weekly_focus_report.html",
        context
    )

def puzzle_zone(request):
    return render(request, "student/puzzle_zone.html")
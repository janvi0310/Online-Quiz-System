from django.shortcuts import render, redirect
from .models import User
from django.contrib.auth.hashers import make_password, check_password
import random
import string
import random
import json
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import Category, Question
from .models import QuizResult
from django.http import JsonResponse
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.db.models import Max, Count



# ================= CAPTCHA GENERATOR =================
def generate_captcha():
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(5))


# ================= REGISTRATION VIEW =================
def register(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if User.objects.filter(username=username).exists():
            return render(request, 'registration.html', {'error': 'Username already exists'})

        User.objects.create(
            username=username,
            email=email,
            password=make_password(password)
        )
        return redirect('login')

    return render(request, 'registration.html')


# ================= LOGIN VIEW =================
# ================= LOGIN VIEW =================
def login(request):
    # Clear any leftover reset_email session
    if 'reset_email' in request.session:
        del request.session['reset_email']

    # Generate CAPTCHA ONLY on GET
    if request.method == "GET":
        request.session['captcha'] = generate_captcha()

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user_captcha = request.POST.get('captcha', '').strip()
        session_captcha = request.session.get('captcha')

        # CAPTCHA validation
        if not session_captcha or user_captcha != session_captcha:
            request.session['captcha'] = generate_captcha()
            return render(request, 'login.html', {'error': 'Invalid CAPTCHA'})

        try:
            user = User.objects.get(username=username)

            if check_password(password, user.password):
                
                request.session['user'] = user.username
                request.session.set_expiry(3600)  # 1 hour session

                del request.session['captcha']  # cleanup
                return redirect('dashboard')
            else:
                request.session['captcha'] = generate_captcha()
                return render(request, 'login.html', {'error': 'Invalid username or password'})

        except User.DoesNotExist:
            request.session['captcha'] = generate_captcha()
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')



# ================= DASHBOARD VIEW =================
def dashboard(request):
    return render(request, 'dashboard.html', {
        'username': request.session.get('user')  # None if logged out
    })


# ================= LOGOUT VIEW =================
def logout(request):
    request.session.flush()   # close session
    return redirect('dashboard')   # redirect to dashboard


# ================= FORGOT PASSWORD VIEW =================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email', '').strip()
        if not User.objects.filter(email=email).exists():
            return render(request, 'forgot_password.html', {'error': 'Email not registered'})
        request.session['reset_email'] = email
        return redirect('reset_password')

    return render(request, 'forgot_password.html')


# ================= RESET PASSWORD VIEW =================
def reset_password(request):
    email = request.session.get('reset_email')
    if not email:
        return redirect('forgot_password')

    if request.method == "POST":
        new_password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if new_password != confirm_password:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match'})

        user = User.objects.get(email=email)
        user.password = make_password(new_password)
        user.save()

        del request.session['reset_email']
        return render(request, 'login.html', {'error': 'Password Changed Successfully'})

    return render(request, 'reset_password.html')


def category(request):
    categories = Category.objects.all()
    return render(request, "category.html", {
        'categories': categories,
        'username': request.session.get('user')
    })


def quiz(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    qs = Question.objects.filter(category=category).order_by('?')[:10]

    questions_json = json.dumps([
        {
            "question": q.question_text,
            "option_A": q.option_a,
            "option_B": q.option_b,
            "option_C": q.option_c,
            "option_D": q.option_d,
            "correct": q.correct_answer
        } for q in qs
    ])

    return render(request, "quiz.html", {
        "category": category,
        "questions_json": questions_json
    })





def leaderboard(request):
    users = QuizResult.objects.all().order_by('-score')  # highest score first

    return render(request, "leaderboard.html", {
        "users": users,
        "username": request.session.get('user')
    })


def save_score(request):
    if request.method == "POST":
        score = int(request.POST.get("score"))
        username = request.session.get("user")

        if not username:
            return JsonResponse({"status": "error", "message": "Not logged in"})

        obj, created = QuizResult.objects.get_or_create(username=username)

        # Only update if new score is better
        if score > obj.score:
            obj.score = score
            obj.date = timezone.now()  # update timestamp
            obj.save()

        return JsonResponse({"status": "success"})
    
def leaderboard(request):
    users = QuizResult.objects.values('username') \
        .annotate(
            best_score=Max('score'),
            quizzes_taken=Count('id'),
            last_active=Max('date')
        ) \
        .order_by('-best_score')

    return render(request, "leaderboard.html", {
        "users": users,
        "username": request.session.get('user')
    })
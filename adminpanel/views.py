from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Category, Question


# ================= DASHBOARD =================
@login_required
def dashboard(request):
    return render(request, 'adminpanel/dashboard.html', {
        'total_categories': Category.objects.count(),
        'total_questions': Question.objects.count(),
    })


# ================= ADD CATEGORY =================
@login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            return redirect('admin_dashboard')

    return render(request, 'adminpanel/add_category.html')


# ================= ADD QUESTION =================
@login_required
def add_question(request):
    categories = Category.objects.all()

    if request.method == "POST":
        category = Category.objects.get(id=request.POST.get('category'))

        Question.objects.create(
            category=category,
            question_text=request.POST.get('question'),
            option1=request.POST.get('option1'),
            option2=request.POST.get('option2'),
            option3=request.POST.get('option3'),
            option4=request.POST.get('option4'),
            correct_answer=request.POST.get('correct_answer')
        )

        return redirect('admin_dashboard')

    return render(request, 'adminpanel/add_question.html', {'categories': categories})


# ================= VIEW QUESTIONS =================
@login_required
def view_questions(request):
    questions = Question.objects.all()
    return render(request, 'adminpanel/view_questions.html', {'questions': questions})


# ================= DELETE QUESTION =================
@login_required
def delete_question(request, id):
    question = get_object_or_404(Question, id=id)
    question.delete()
    return redirect('view_questions')

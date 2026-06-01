from django.contrib import admin
from .models import Category, Question,QuizResult

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question_text', 'category', 'correct_answer')
    list_filter = ('category',)
    search_fields = ('question_text',)


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('username', 'score', 'date')
    list_filter = ('date',)
    search_fields = ('username',)
    ordering = ('-date',)
                     
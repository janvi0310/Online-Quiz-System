from django.urls import path
from . import views

urlpatterns = [
    path('adminpanel', views.dashboard, name='admin_dashboard'),
    path('add-category/', views.add_category, name='add_category'),
    path('add-question/', views.add_question, name='add_question'),
    path('view-questions/', views.view_questions, name='view_questions'),
    path('delete-question/<int:id>/', views.delete_question, name='delete_question'),
]

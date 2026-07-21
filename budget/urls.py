from django.urls import path
from . import views

urlpatterns = [
    path('', views.budget_list, name='budget_list'),
    path('set/', views.budget_add_or_edit, name='budget_set'),
    path('edit/<int:pk>/', views.budget_add_or_edit, name='budget_edit'),
    path('delete/<int:pk>/', views.budget_delete, name='budget_delete'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.income_list, name='income_list'),
    path('add/', views.income_add, name='income_add'),
    path('edit/<int:pk>/', views.income_edit, name='income_edit'),
    path('delete/<int:pk>/', views.income_delete, name='income_delete'),
]

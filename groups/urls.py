from django.urls import path
from . import views

urlpatterns = [
    path('', views.group_list_view, name='group_list'),
    path('<int:group_id>/', views.group_detail_view, name='group_detail'),
    path('<int:group_id>/expense/add/', views.group_expense_add_view, name='group_expense_add'),
    path('<int:group_id>/expense/<int:expense_id>/delete/', views.group_expense_delete_view, name='group_expense_delete'),
    path('<int:group_id>/settle/', views.settle_payment_view, name='settle_payment'),
]

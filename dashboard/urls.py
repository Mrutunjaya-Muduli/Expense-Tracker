from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
]

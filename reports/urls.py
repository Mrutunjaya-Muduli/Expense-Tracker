from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]

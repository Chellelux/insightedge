from django.urls import path
from . import dashboard_views

app_name = 'reports'

urlpatterns = [
    path('', dashboard_views.dashboard, name='dashboard'),
    path('students/', dashboard_views.student_list, name='student_list'),
    path('students/<int:pk>/', dashboard_views.student_detail, name='student_detail'),
    path('reports/', dashboard_views.report_list, name='report_list'),
    path('reports/<int:pk>/', dashboard_views.report_detail, name='report_detail'),
    path('analytics/', dashboard_views.analytics, name='analytics'),
]
from django.contrib import admin
from .models import AnalyticsDashboard, StudentMetrics


@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_students', 'at_risk_students', 'high_risk_students', 'average_gpa']
    list_filter = ['date']
    date_hierarchy = 'date'


@admin.register(StudentMetrics)
class StudentMetricsAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'gpa', 'attendance_rate', 'risk_score']
    list_filter = ['date']
    search_fields = ['student__student_id']
    date_hierarchy = 'date'


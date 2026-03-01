from django.contrib import admin
from .models import Student, CourseEnrollment, StudentActivity


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'first_name', 'last_name', 'email', 'major', 'year_level', 'gpa', 'overall_risk_score', 'assigned_counselor']
    list_filter = ['year_level', 'major', 'is_active']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    list_editable = ['assigned_counselor']
    readonly_fields = ['overall_risk_score', 'last_risk_assessment']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course_code', 'course_name', 'professor', 'semester', 'current_grade', 'attendance_rate']
    list_filter = ['semester', 'current_grade', 'is_active']
    search_fields = ['student__student_id', 'course_code', 'course_name']


@admin.register(StudentActivity)
class StudentActivityAdmin(admin.ModelAdmin):
    list_display = ['student', 'activity_type', 'title', 'date', 'score', 'recorded_by']
    list_filter = ['activity_type', 'date']
    search_fields = ['student__student_id', 'title', 'description']
    date_hierarchy = 'date'


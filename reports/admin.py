from django.contrib import admin
from .models import RiskReport, ReportComment, Intervention, CollaborationNote


@admin.register(RiskReport)
class RiskReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'risk_level', 'risk_score', 'status', 'created_at', 'assigned_to']
    list_filter = ['risk_level', 'status', 'created_at']
    search_fields = ['student__student_id', 'student__first_name', 'student__last_name']
    readonly_fields = ['created_at', 'updated_at', 'reviewed_at', 'resolved_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Student Information', {
            'fields': ('student', 'created_by', 'assigned_to')
        }),
        ('Risk Assessment', {
            'fields': ('risk_level', 'risk_score', 'academic_risk', 'attendance_risk', 'engagement_risk', 'behavioral_risk')
        }),
        ('AI Analysis', {
            'fields': ('ai_summary', 'ai_indicators', 'ai_recommendations')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'reviewed_at', 'resolved_at')
        }),
    )


@admin.register(ReportComment)
class ReportCommentAdmin(admin.ModelAdmin):
    list_display = ['report', 'author', 'is_private', 'created_at']
    list_filter = ['is_private', 'created_at']
    search_fields = ['content', 'author__username']


@admin.register(Intervention)
class InterventionAdmin(admin.ModelAdmin):
    list_display = ['report', 'intervention_type', 'title', 'status', 'scheduled_date', 'conducted_by']
    list_filter = ['intervention_type', 'status', 'scheduled_date']
    search_fields = ['title', 'description']
    date_hierarchy = 'scheduled_date'


@admin.register(CollaborationNote)
class CollaborationNoteAdmin(admin.ModelAdmin):
    list_display = ['student', 'author', 'title', 'is_urgent', 'is_private', 'created_at']
    list_filter = ['is_urgent', 'is_private', 'created_at']
    search_fields = ['title', 'content', 'student__student_id']
    date_hierarchy = 'created_at'
# Register your models here.

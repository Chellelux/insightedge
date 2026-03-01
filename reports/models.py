from django.db import models
from django.conf import settings
from students.models import Student

class RiskReport(models.Model):
    """AI-generated risk assessment reports"""

    RISK_LEVELS = [
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
        ('critical', 'Critical Risk'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='risk_reports')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS)
    risk_score = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # AI Analysis
    ai_summary = models.TextField()
    ai_indicators = models.JSONField(default=dict)
    ai_recommendations = models.TextField()

    # Risk Factors
    academic_risk = models.FloatField(default=0.0)
    attendance_risk = models.FloatField(default=0.0)
    engagement_risk = models.FloatField(default=0.0)
    behavioral_risk = models.FloatField(default=0.0)

    # Assignment
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_reports'
    )

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.student_id} - {self.risk_level} - {self.created_at.date()}"


class ReportComment(models.Model):
    """Collaboration comments on risk reports"""

    report = models.ForeignKey(RiskReport, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_private = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.report.id}"


class Intervention(models.Model):
    """Intervention actions taken for at-risk students"""

    INTERVENTION_TYPES = [
        ('meeting', 'One-on-One Meeting'),
        ('tutoring', 'Tutoring Referral'),
        ('counseling', 'Counseling Session'),
        ('academic_plan', 'Academic Plan'),
        ('peer_support', 'Peer Support'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]

    report = models.ForeignKey(RiskReport, on_delete=models.CASCADE, related_name='interventions')
    intervention_type = models.CharField(max_length=20, choices=INTERVENTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    conducted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interventions_conducted'
    )

    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)
    outcome_notes = models.TextField(blank=True)
    follow_up_required = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.intervention_type} - {self.report.student.student_id}"


class CollaborationNote(models.Model):
    """Shared notes between professors and counselors"""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='collaboration_notes')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_urgent = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_notes',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.student.student_id}"


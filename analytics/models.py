from django.db import models
from students.models import Student

class AnalyticsDashboard(models.Model):
    """Dashboard snapshot for analytics"""

    date = models.DateField(unique=True)
    total_students = models.IntegerField(default=0)
    at_risk_students = models.IntegerField(default=0)
    high_risk_students = models.IntegerField(default=0)
    average_gpa = models.FloatField(default=0.0)
    average_attendance = models.FloatField(default=0.0)
    reports_generated = models.IntegerField(default=0)
    interventions_completed = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Dashboard - {self.date}"


class StudentMetrics(models.Model):
    """Historical metrics for student performance tracking"""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    gpa = models.FloatField()
    attendance_rate = models.FloatField()
    risk_score = models.FloatField()
    engagement_score = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['student', 'date']

    def __str__(self):
        return f"{self.student.student_id} - {self.date}"


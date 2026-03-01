from django.db import models

from django.conf import settings

class Student(models.Model):
    """Student model"""

    YEAR_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
        ('5', 'Fifth Year'),
    ]

    student_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    year_level = models.CharField(max_length=1, choices=YEAR_CHOICES)
    major = models.CharField(max_length=100)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    enrollment_date = models.DateField()
    profile_picture = models.ImageField(upload_to='student_profiles/', null=True, blank=True)
    
    # Academic tracking
    current_credits = models.IntegerField(default=0)
    total_credits = models.IntegerField(default=0)
    
    # Contact information
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Assignment
    assigned_counselor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_students',
        limit_choices_to={'user_type': 'counselor'}
    )
    
    # Risk tracking
    overall_risk_score = models.FloatField(default=0.0)
    last_risk_assessment = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student_id} - {self.first_name} {self.last_name}"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class CourseEnrollment(models.Model):
    """Course enrollment tracking"""

    GRADE_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
        ('W', 'Withdrawn'),
        ('I', 'Incomplete'),
        ('P', 'In Progress'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=200)
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses',
        limit_choices_to={'user_type': 'professor'}
    )
    semester = models.CharField(max_length=50)
    credits = models.IntegerField(default=3)
    current_grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='P')
    attendance_rate = models.FloatField(default=100.0)
    assignments_completed = models.IntegerField(default=0)
    assignments_total = models.IntegerField(default=0)
    enrolled_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-enrolled_date']
        unique_together = ['student', 'course_code', 'semester']

    def __str__(self):
        return f"{self.student.student_id} - {self.course_code}"

    @property
    def completion_rate(self):
        if self.assignments_total == 0:
            return 0
        return (self.assignments_completed / self.assignments_total) * 100


class StudentActivity(models.Model):
    """Track student activities and behaviors"""

    ACTIVITY_TYPES = [
        ('attendance', 'Attendance'),
        ('assignment', 'Assignment'),
        ('exam', 'Exam'),
        ('participation', 'Participation'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course = models.ForeignKey(CourseEnrollment, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    score = models.FloatField(null=True, blank=True)
    max_score = models.FloatField(null=True, blank=True)
    date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Student Activities'

    def __str__(self):
        return f"{self.student.student_id} - {self.activity_type} - {self.title}"

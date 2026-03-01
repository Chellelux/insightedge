from django.db import models
from django.db import models

class User(AbstractUser):
    """Custom user model for InsightEdge"""
    
    USER_TYPE_CHOICES = [
        ('professor', 'Professor'),
        ('counselor', 'Counselor'),
        ('admin', 'Administrator'),
    ]
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.user_type})"


class Notification(models.Model):
    """Notification model for user alerts"""
    
    NOTIFICATION_TYPES = [
        ('risk_alert', 'Risk Alert'),
        ('new_report', 'New Report'),
        ('comment', 'Comment'),
        ('assignment', 'Assignment'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.recipient.username}"
# Create your models here.

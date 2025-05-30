# models.py - Add indexes and constraints
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AutomationRule(models.Model):
    CONDITION_CHOICES = [
        ('CPU_HIGH', 'High CPU Usage'),
        ('MEMORY_HIGH', 'High Memory Usage'),
        ('DISK_HIGH', 'High Disk Usage'),
        ('IP_SUSPICIOUS', 'Suspicious IP Detected'),
    ]

    ACTION_CHOICES = [
        ('EMAIL_ALERT', 'Send Email Alert'),
        ('BLOCK_IP', 'Block IP'),
        ('LOG_ONLY', 'Log Only'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES)
    threshold = models.FloatField()
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'active']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(threshold__gte=0),
                name='threshold_positive'
            )
        ]

class ActionLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    condition = models.CharField(max_length=50)
    value = models.FloatField()
    action_taken = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']
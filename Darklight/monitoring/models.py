# models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SystemMetrics(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='system_metrics')
    cpu_usage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    memory_usage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )
    disk_usage = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
        ordering = ['-created_at']

class PingResult(TimestampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ping_results')
    target_ip = models.GenericIPAddressField()
    reachable = models.BooleanField()
    latency = models.FloatField(null=True, blank=True)  # in milliseconds
    packet_loss = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['target_ip']),
        ]
        ordering = ['-created_at']
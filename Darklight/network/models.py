from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class NetworkDevice(models.Model):
    """Represents a network device being monitored"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'ip_address']),
            models.Index(fields=['is_active']),
        ]
        unique_together = ['user', 'ip_address']

    def __str__(self):
        return f"{self.name} ({self.ip_address})"

class NetworkScan(models.Model):
    """Records results of network scans"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scans')
    device = models.ForeignKey(NetworkDevice, on_delete=models.CASCADE)
    latency = models.FloatField(help_text="Latency in milliseconds") 
    packet_loss = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage of packet loss"
    )
    scan_time = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField()

    class Meta:
        ordering = ['-scan_time']
        get_latest_by = 'scan_time'
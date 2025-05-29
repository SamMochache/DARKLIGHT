# serializers.py
from rest_framework import serializers
from .models import SystemMetrics, PingResult

class SystemMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemMetrics
        fields = ['id', 'cpu_usage', 'memory_usage', 'disk_usage', 'created_at']
        read_only_fields = fields

class PingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = PingResult
        fields = ['id', 'target_ip', 'reachable', 'latency', 'packet_loss', 'created_at']
        read_only_fields = fields
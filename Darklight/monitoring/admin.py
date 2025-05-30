# admin.py
from django.contrib import admin
from .models import SystemMetrics, PingResult

@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = ('user', 'cpu_usage', 'memory_usage', 'disk_usage', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(PingResult)
class PingResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_ip', 'reachable', 'latency', 'created_at')
    list_filter = ('reachable', 'target_ip', 'created_at')
    search_fields = ('user__username', 'target_ip')
    readonly_fields = ('created_at', 'updated_at')


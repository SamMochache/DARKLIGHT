from django.contrib import admin
from .models import NetworkDevice, NetworkScan

@admin.register(NetworkDevice)
class NetworkDeviceAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip_address', 'user', 'is_active')
    list_filter = ('is_active', 'user')
    search_fields = ('name', 'ip_address')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(NetworkScan)
class NetworkScanAdmin(admin.ModelAdmin):
    list_display = ('device', 'latency', 'packet_loss', 'is_successful', 'scan_time')
    list_filter = ('is_successful', 'device__user')
    readonly_fields = ('scan_time',)
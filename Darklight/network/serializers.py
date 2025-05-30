from rest_framework import serializers
from .models import NetworkDevice, NetworkScan

class NetworkDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkDevice
        fields = ['id', 'name', 'ip_address', 'mac_address', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

class NetworkScanSerializer(serializers.ModelSerializer):
    device = NetworkDeviceSerializer(read_only=True)
    
    class Meta:
        model = NetworkScan
        fields = ['id', 'device', 'latency', 'packet_loss', 'is_successful', 'scan_time']
        read_only_fields = fields
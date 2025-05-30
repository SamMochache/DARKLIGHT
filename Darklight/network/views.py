from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import NetworkDevice, NetworkScan
from .serializers import NetworkDeviceSerializer, NetworkScanSerializer
from .utils import perform_network_scan

class NetworkDeviceListCreateView(generics.ListCreateAPIView):
    serializer_class = NetworkDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NetworkDevice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class NetworkDeviceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NetworkDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NetworkDevice.objects.filter(user=self.request.user)

class NetworkScanView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        device_id = request.data.get('device_id')
        try:
            device = NetworkDevice.objects.get(id=device_id, user=request.user)
            scan_result = perform_network_scan(device.ip_address)
            scan = NetworkScan.objects.create(
                user=request.user,
                device=device,
                **scan_result
            )
            return Response(
                NetworkScanSerializer(scan).data,
                status=status.HTTP_201_CREATED
            )
        except NetworkDevice.DoesNotExist:
            return Response(
                {"error": "Device not found"},
                status=status.HTTP_404_NOT_FOUND
            )

class NetworkScanHistoryView(generics.ListAPIView):
    serializer_class = NetworkScanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NetworkScan.objects.filter(
            user=self.request.user
        ).order_by('-scan_time')[:100]  # Limit to 100 most recent scans
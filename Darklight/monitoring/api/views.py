# api/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from monitoring.models import SystemMetrics, PingResult
from monitoring.serializers import SystemMetricsSerializer, PingResultSerializer
from monitoring.utils.monitoring import SystemMonitor, NetworkMonitor

class MetricsCollectionThrottle(UserRateThrottle):
    rate = '5/minute'

class CollectMetricsView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [MetricsCollectionThrottle]

    def create(self, request, *args, **kwargs):
        metric = SystemMonitor.collect_metrics(request.user)
        if metric:
            return Response(
                SystemMetricsSerializer(metric).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"error": "Failed to collect metrics"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class PingIPView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PingResultSerializer

    def create(self, request, *args, **kwargs):
        ip = request.data.get("ip")
        if not ip:
            return Response(
                {"error": "IP address is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = NetworkMonitor.ping_ip(request.user, ip)
        return Response(
            PingResultSerializer(result).data,
            status=status.HTTP_201_CREATED
        )

class MetricsHistoryView(generics.ListAPIView):
    serializer_class = SystemMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Or use PageNumberPagination with small page size

    def get_queryset(self):
        return SystemMetrics.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:100]  # Limit to 100 most recent

class PingHistoryView(generics.ListAPIView):
    serializer_class = PingResultSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['target_ip', 'reachable']

    def get_queryset(self):
        return PingResult.objects.filter(
            user=self.request.user
        ).order_by('-created_at')[:100]
from django.urls import path
from rest_framework.routers import DefaultRouter
from .api.views import (
    CollectMetricsView,
    PingIPView,
    MetricsHistoryView,
    PingHistoryView
)

app_name = 'monitoring'

# Using DRF's DefaultRouter for better API exploration
router = DefaultRouter()

urlpatterns = [
    # System Metrics Endpoints
    path('metrics/collect/', CollectMetricsView.as_view(), name='collect-metrics'),
    path('metrics/history/', MetricsHistoryView.as_view(), name='metrics-history'),
    
    # Network Monitoring Endpoints
    path('network/ping/', PingIPView.as_view(), name='ping-ip'),
    path('network/history/', PingHistoryView.as_view(), name='ping-history'),
]

urlpatterns += router.urls
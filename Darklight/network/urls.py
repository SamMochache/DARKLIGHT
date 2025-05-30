from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    NetworkDeviceListCreateView,
    NetworkDeviceDetailView,
    NetworkScanView,
    NetworkScanHistoryView
)

router = DefaultRouter()

urlpatterns = [
    path('devices/', NetworkDeviceListCreateView.as_view(), name='networkdevice-list'),
    path('devices/<int:pk>/', NetworkDeviceDetailView.as_view(), name='networkdevice-detail'),
    path('scan/', NetworkScanView.as_view(), name='networkscan-list'),
    path('history/', NetworkScanHistoryView.as_view(), name='networkscan-history'),
]

urlpatterns += router.urls
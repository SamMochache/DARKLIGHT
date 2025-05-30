import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import SystemMetrics, PingResult
from .utils.monitoring import SystemMonitor, NetworkMonitor

User = get_user_model()

# -----------------------
# Pytest Fixtures
# -----------------------

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

# -----------------------
# Unit Tests (Monitoring Logic)
# -----------------------

class TestMonitoringUtils:
    @pytest.mark.django_db
    def test_collect_metrics(self, user):
        metric = SystemMonitor.collect_metrics(user)
        assert metric is not None
        assert 0 <= metric.cpu_usage <= 100
        assert 0 <= metric.memory_usage <= 100
        assert 0 <= metric.disk_usage <= 100

    @pytest.mark.django_db
    def test_ping_ip(self, user):
        result = NetworkMonitor.ping_ip(user, "8.8.8.8")
        assert result.reachable is True
        assert result.latency > 0

        result = NetworkMonitor.ping_ip(user, "192.0.2.0")  # Test-Net IP
        assert result.reachable is False

# -----------------------
# API Tests
# -----------------------

class MonitoringAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Clean DB to ensure isolation
        SystemMetrics.objects.all().delete()
        PingResult.objects.all().delete()

        # Setup test data
        SystemMetrics.objects.create(
            user=self.user,
            cpu_usage=25.5,
            memory_usage=45.0,
            disk_usage=30.0
        )
        PingResult.objects.create(
            user=self.user,
            target_ip="8.8.8.8",
            reachable=True,
            latency=12.5
        )

    # --- System Metrics ---
    def test_collect_metrics(self):
        response = self.client.post('/api/monitoring/metrics/collect/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('cpu_usage', response.data)

    def test_metrics_history(self):
        response = self.client.get('/api/monitoring/metrics/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(float(response.data[0]['cpu_usage']), 25.5)

    # --- Network ---
    @patch('monitoring.utils.monitoring.NetworkMonitor.ping_ip')
    def test_ping_ip(self, mock_ping):
        mock_ping.return_value = PingResult(user=self.user, target_ip="8.8.8.8", reachable=True, latency=10)
        response = self.client.post('/api/monitoring/network/ping/', {'ip': '8.8.8.8'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['reachable'])

    def test_ping_history(self):
        response = self.client.get('/api/monitoring/network/history/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['target_ip'], "8.8.8.8")

    # --- Security ---
    def test_unauthenticated_access(self):
        self.client.logout()
        endpoints = [
            '/api/monitoring/metrics/collect/',
            '/api/monitoring/metrics/history/',
            '/api/monitoring/network/ping/',
            '/api/monitoring/network/history/'
        ]
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --- Throttling ---
    @override_settings(
        REST_FRAMEWORK={
            'DEFAULT_THROTTLE_CLASSES': [
                'rest_framework.throttling.UserRateThrottle',
            ],
            'DEFAULT_THROTTLE_RATES': {
                'user': '2/min',
            }
        }
    )
    def test_metrics_collection_throttling(self):
        # First two allowed
        self.client.post('/api/monitoring/metrics/collect/')
        self.client.post('/api/monitoring/metrics/collect/')
        # Third should be blocked
        response = self.client.post('/api/monitoring/metrics/collect/')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

# -----------------------
# Celery Task Tests
# -----------------------

@pytest.mark.django_db
class TestMonitoringTasks:
    def test_monitor_user_systems(self, user):
        from monitoring.tasks import monitor_user_systems
        monitor_user_systems()
        assert SystemMetrics.objects.filter(user=user).exists()

    def test_monitor_network_targets(self, user):
        from monitoring.tasks import monitor_network_targets
        monitor_network_targets()
        assert PingResult.objects.filter(user=user).exists()

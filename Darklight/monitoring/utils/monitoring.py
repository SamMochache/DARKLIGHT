# utils/monitoring.py
import psutil
from ping3 import ping, verbose_ping
from datetime import datetime
from django.utils.timezone import now
from monitoring.models import SystemMetrics, PingResult

class SystemMonitor:
    @staticmethod
    def collect_metrics(user):
        """Collect system metrics with error handling"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent

            return SystemMetrics.objects.create(
                user=user,
                cpu_usage=cpu,
                memory_usage=memory,
                disk_usage=disk,
            )
        except Exception as e:
            # Implement proper error logging here
            return None

class NetworkMonitor:
    @staticmethod
    def ping_ip(user, ip, count=3, timeout=2):
        """Enhanced ping with multiple attempts and packet loss calculation"""
        try:
            results = []
            success_count = 0
            
            for _ in range(count):
                latency = ping(ip, timeout=timeout, unit='ms')
                if latency is not None:
                    success_count += 1
                    results.append(latency)
            
            packet_loss = ((count - success_count) / count) * 100
            avg_latency = sum(results) / len(results) if results else None

            return PingResult.objects.create(
                user=user,
                target_ip=ip,
                reachable=success_count > 0,
                latency=avg_latency,
                packet_loss=packet_loss
            )
        except Exception as e:
            return PingResult.objects.create(
                user=user,
                target_ip=ip,
                reachable=False,
                latency=None,
                packet_loss=100
            )
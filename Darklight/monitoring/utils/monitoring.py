# utils/monitoring.py
import psutil
import subprocess
import re
import socket
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
    def ping_ip(user, ip):
        try:
            # Ping once (Linux/Mac). On Windows use '-n 1'
            output = subprocess.check_output(
                ['ping', '-c', '1', ip],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                timeout=3
            )
            # Check if packet received
            reachable = bool(re.search(r'1 packets? received', output) or re.search(r'1 received', output))
            latency = NetworkMonitor._extract_latency(output) if reachable else 0
            return PingResult(user=user, target_ip=ip, reachable=reachable, latency=latency)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            # ICMP ping failed or timed out, fallback to TCP socket check on port 80
            try:
                sock = socket.create_connection((ip, 80), timeout=2)
                sock.close()
                return PingResult(user=user, target_ip=ip, reachable=True, latency=0)
            except Exception:
                # TCP connection failed - unreachable
                return PingResult(user=user, target_ip=ip, reachable=False, latency=0)
        except Exception:
            # Any unexpected error: treat as unreachable
            return PingResult(user=user, target_ip=ip, reachable=False, latency=0)

    @staticmethod
    def _extract_latency(ping_output):
        match = re.search(r'time=(\d+\.?\d*) ms', ping_output)
        if match:
            return float(match.group(1))
        return 0
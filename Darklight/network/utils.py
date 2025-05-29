import subprocess
from ping3 import ping
from datetime import datetime

def perform_network_scan(ip_address):
    """Enhanced network scanning with multiple checks"""
    try:
        # Perform ping test
        latency = ping(ip_address, timeout=2, unit='ms')
        reachable = latency is not None
        
        # Perform traceroute (optional)
        trace = subprocess.run(
            ['traceroute', ip_address],
            capture_output=True,
            text=True
        )
        
        return {
            'latency': latency if reachable else 0.0,
            'packet_loss': 0.0 if reachable else 100.0,
            'is_successful': reachable,
            'traceroute': trace.stdout if trace.returncode == 0 else None
        }
    except Exception as e:
        return {
            'latency': 0.0,
            'packet_loss': 100.0,
            'is_successful': False,
            'error': str(e)
        }
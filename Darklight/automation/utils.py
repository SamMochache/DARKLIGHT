# utils.py - Add error handling and logging
import logging
from automation.models import AutomationRule, ActionLog
from monitoring.models import SystemMetrics
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

def check_and_apply_rules(user):
    try:
        rules = AutomationRule.objects.filter(user=user, active=True)
        if not rules.exists():
            return

        latest_metrics = SystemMetrics.objects.filter(user=user).last()
        if not latest_metrics:
            return

        for rule in rules:
            triggered = False
            value = 0.0

            condition_map = {
                'CPU_HIGH': latest_metrics.cpu_usage,
                'MEMORY_HIGH': latest_metrics.memory_usage,
                'DISK_HIGH': latest_metrics.disk_usage,
            }

            if rule.condition in condition_map:
                value = condition_map[rule.condition]
                triggered = value >= rule.threshold

            if triggered:
                action_handlers = {
                    'EMAIL_ALERT': lambda: send_alert_email(user, rule, value),
                    'BLOCK_IP': lambda: block_ip_action(user, rule, value),
                }
                
                action_desc = action_handlers.get(rule.action, lambda: "Logged condition only")()

                ActionLog.objects.create(
                    user=user,
                    condition=rule.condition,
                    value=value,
                    action_taken=action_desc
                )
    except Exception as e:
        logger.error(f"Failed to apply rules for user {user.id}: {str(e)}")
        raise

def send_alert_email(user, rule, value):
    send_mail(
        subject="CyberTiba Alert",
        message=f"{rule.condition} exceeded: {value}%",
        from_email="alerts@cybertiba.ke",
        recipient_list=[user.email],
        fail_silently=True
    )
    return f"Email sent to {user.email}"

def block_ip_action(user, rule, value):
    # Implement actual IP blocking logic here
    return f"Blocked suspicious IP (mock)"
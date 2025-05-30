# serializers.py - Add validation and security
from rest_framework import serializers
from automation.models import AutomationRule, ActionLog

class AutomationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationRule
        fields = '__all__'
        read_only_fields = ('user',)
        
    def validate_threshold(self, value):
        if value <= 0:
            raise serializers.ValidationError("Threshold must be positive")
        return value

class ActionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionLog
        fields = '__all__'
        read_only_fields = ('user', 'timestamp')
# admin.py - Add admin interfaces
from django.contrib import admin
from automation.models import AutomationRule, ActionLog

@admin.register(AutomationRule)
class AutomationRuleAdmin(admin.ModelAdmin):
    list_display = ('user', 'condition', 'threshold', 'action', 'active')
    list_filter = ('condition', 'action', 'active')
    search_fields = ('user__username', 'condition')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ActionLog)
class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'condition', 'value', 'action_taken', 'timestamp')
    list_filter = ('condition',)
    search_fields = ('user__username', 'action_taken')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
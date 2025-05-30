# views.py - Add pagination and filtering
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from automation.models import AutomationRule, ActionLog
from automation.serializers import AutomationRuleSerializer, ActionLogSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
class RuleListCreateView(generics.ListCreateAPIView):
    serializer_class = AutomationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['condition', 'active']
    search_fields = ['condition']
    ordering_fields = ['threshold']

    def get_queryset(self):
        return AutomationRule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ActionLogListView(generics.ListAPIView):
    serializer_class = ActionLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['condition']
    ordering_fields = ['timestamp']

    def get_queryset(self):
        return ActionLog.objects.filter(user=self.request.user)
    
class AutomationRuleViewSet(viewsets.ModelViewSet):
    """
    A complete ViewSet for AutomationRule with all CRUD operations,
    pagination, and advanced filtering.
    """
    serializer_class = AutomationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = {
        'condition': ['exact', 'in'],
        'active': ['exact'],
        'threshold': ['gte', 'lte', 'exact']
    }
    search_fields = ['condition', 'action']
    ordering_fields = ['threshold', 'condition', 'action']
    ordering = ['-id']

    def get_queryset(self):
        return AutomationRule.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Custom action to toggle rule active status"""
        rule = self.get_object()
        rule.active = not rule.active
        rule.save()
        return Response({'status': 'toggled', 'active': rule.active})
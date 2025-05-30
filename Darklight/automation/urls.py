from django.urls import path, include
from django.http import HttpResponse
from rest_framework.routers import DefaultRouter
from automation.views import (
    RuleListCreateView, 
    RuleRetrieveUpdateDestroyView,  # Add this import
    ActionLogListView, 
    AutomationRuleViewSet
)

# Initialize router
router = DefaultRouter()
router.register(r'rules', AutomationRuleViewSet, basename='rule')  # Changed endpoint to 'rules'

urlpatterns = [
    # Versioned API endpoints
    path('api/v1/', include([
        # Standard endpoints (kept for backward compatibility)
        path('rules-legacy/', RuleListCreateView.as_view(), name='rule-legacy-list'),
        path('rules-legacy/<int:pk>/', RuleRetrieveUpdateDestroyView.as_view(), name='rule-legacy-detail'),
        
        # ViewSet endpoints (recommended)
        path('', include(router.urls)),
        
        # Logs endpoint
        path('logs/', ActionLogListView.as_view(), name='action-log-list'),
        
        # Health Check
        path('health/', lambda request: HttpResponse(status=200), name='health-check'),
    ])),
    
    # Authentication
    path('api/auth/', include('rest_framework.urls')),
]
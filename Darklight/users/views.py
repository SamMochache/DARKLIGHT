from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import CustomUser
from .serializers import RegisterSerializer, CustomUserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .tasks import send_verification_email

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Cache user data to reduce DB hits
        user_data = CustomUserSerializer(self.user).data
        cache_key = f'user_{self.user.id}_auth'
        cache.set(cache_key, user_data, timeout=3600)  # Cache for 1 hour
        
        data['user'] = user_data
        return data

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        
        # Send verification email asynchronously
        send_verification_email.delay(user.id)

@method_decorator(cache_page(60*5), name='dispatch')  # Cache profile for 5 minutes
class ProfileView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
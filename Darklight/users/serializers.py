from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from .models import CustomUser

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, 
                                   validators=[validate_password],
                                   style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True,
                                    style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'password2', 'phone']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        
        email = attrs.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "User with this email already exists"})
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone', 'last_login']
        read_only_fields = ['id', 'last_login']
        
    def to_representation(self, instance):
        # Cache user data for frequent profile requests
        cache_key = f'user_{instance.id}_profile'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
            
        data = super().to_representation(instance)
        cache.set(cache_key, data, timeout=300)  # Cache for 5 minutes
        return data
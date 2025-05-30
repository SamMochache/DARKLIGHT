from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class UserTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        
        # Proper test user data including all required fields
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Complexpass123!',
            'password2': 'Complexpass123!',
            'phone': '+254712345678'  # Add if your serializer requires it
        }
        
        self.login_data = {
            'email': 'test@example.com',
            'password': 'Complexpass123!'
        }

    def test_user_registration(self):
        """Test user registration with valid data"""
        response = self.client.post(
            self.register_url, 
            self.user_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_user_login(self):
        """Test JWT token authentication"""
        # First register the user
        self.client.post(self.register_url, self.user_data, format='json')
        
        # Then test login
        response = self.client.post(
            self.login_url,
            self.login_data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_profile_caching(self):
        """Test profile endpoint caching"""
        # Register and login
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, self.login_data, format='json')
        
        # Set auth token
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # First profile request
        response1 = self.client.get(self.profile_url)
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verify cache
        user = User.objects.get(email=self.user_data['email'])
        cache_key = f'user_{user.id}_profile'
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
        self.assertEqual(cached_data['email'], user.email)
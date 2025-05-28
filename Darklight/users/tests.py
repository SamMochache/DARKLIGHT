from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser
from django.core.cache import cache

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'Testpass123',
            'password2': 'Testpass123',
            'phone': '+1234567890'
        }
        
    def test_user_registration(self):
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 1)
        
    def test_user_login(self):
        # First register
        self.client.post(reverse('register'), self.user_data, format='json')
        
        # Then login
        login_data = {
            'email': 'test@example.com',
            'password': 'Testpass123'
        }
        response = self.client.post(reverse('login'), login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_user_profile_caching(self):
        # Register and login
        self.client.post(reverse('register'), self.user_data, format='json')
        login_data = {
            'email': 'test@example.com',
            'password': 'Testpass123'
        }
        login_response = self.client.post(reverse('login'), login_data, format='json')
        token = login_response.data['access']
        
        # Test profile caching
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response1 = self.client.get(reverse('profile'))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Verify cache was set
        user = CustomUser.objects.get(email='test@example.com')
        cache_key = f'user_{user.id}_profile'
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
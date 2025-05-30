from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import NetworkDevice

User = get_user_model()

class NetworkTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='network@test.com',
            username='networkuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.device = NetworkDevice.objects.create(
            user=self.user,
            name='Test Router',
            ip_address='192.168.1.1'
        )

    def test_create_device(self):
        url = reverse('networkdevice-list')
        data = {
            'name': 'New Device',
            'ip_address': '192.168.1.2'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(NetworkDevice.objects.count(), 2)

    def test_scan_device(self):
        url = reverse('networkscan-list')
        response = self.client.post(url, {'device_id': self.device.id}, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_502_BAD_GATEWAY])

    def test_device_history(self):
        url = reverse('networkscan-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access(self):
        self.client.logout()
        urls = [
            reverse('networkdevice-list'),
            reverse('networkscan-list')
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
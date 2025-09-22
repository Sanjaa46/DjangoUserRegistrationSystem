from rest_framework.test import APITestCase
from rest_framework import status
from .models import User 
from django.urls import reverse


class RegisterationTestCase(APITestCase):
    def test_registeration(self):
        url = reverse('register')
        data = {
            "username": "testuser",
            "email": "testuser@gmail.com",
            "password": "Testpass123",
            "password2": "Testpass123",
            "first_name": "Test",
            "last_name": "User",
            "bio": "This is a test user."
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_registeration_duplicate_email(self):
        User.objects.create_user(username="existing", email="testuser@gmail.com", password="Testpass123")
        url = reverse('register')
        data = {
            "username": "newuser",
            "email": "testuser@gmail.com",
            "password": "Testpass123",
            "password2": "Testpass123",
            "first_name": "Existing",
            "last_name": "User",
            "bio": "This is a existing email test user."
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

class UserTests(APITestCase):

    def setUp(self):
        # Runs before every test
        self.user = User.objects.create_user(username="testuser", email="test@gmail.com", password="Testpass123")
        self.admin = User.objects.create_superuser(username="admin", email="admin@gmail.com", password="Adminpass123")

    def test_login(self):
        url = reverse('token_obtain_pair')
        data = {"username": "testuser", "password": "Testpass123"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_get(self):
        # Login first
        url = reverse('token_obtain_pair')
        login_resp = self.client.post(url, {"username": "testuser", "password": "Testpass123"}, format='json')
        token = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Test GET /profile/
        url = reverse('user_detail')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['username'], 'testuser')

    def test_profile_patch(self):
        url = reverse('token_obtain_pair')
        login_resp = self.client.post(url, {"username": "testuser", "password": "Testpass123"}, format='json')
        token = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Test PATCH /profile/
        url = reverse('user_detail')
        resp = self.client.patch(url, {"password": "NewPass456", "email": "changed@gmail.com"}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Fetch updated user from DB
        user = User.objects.get(username="testuser")

        # Check email updated
        self.assertEqual(user.email, "changed@gmail.com")

        # Check password updated correctly
        self.assertTrue(user.check_password("NewPass456"))

    def test_profile_delete(self):
        url = reverse('token_obtain_pair')
        login_resp = self.client.post(url, {"username": "testuser", "password": "Testpass123"}, format='json')
        token = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Test DELETE /profile/
        url = reverse('user_detail')
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.filter(username="testuser").count(), 0)

    def test_admin_can_lists_users(self):
        url = reverse('token_obtain_pair')
        login_resp = self.client.post(url, {"username": "admin", "password": "Adminpass123"}, format = 'json')
        token = login_resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Test GET /users/
        url = reverse('user_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 2)


from django.utils import timezone
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase


class UserDetailViewTests(TestCase):
    def test_get_user_detail(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        response = self.client.get(f"/accounts/users/{user.username}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/user_detail.html")

    def test_user_detail_contains_user_data(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        user.last_login = timezone.now()
        user.save()
        response = self.client.get(f"/accounts/users/{user.username}")
        self.assertContains(response, f"{user.username}", html=True)
        self.assertContains(response, f"Last activity: {user.last_login.strftime('%B %d, %Y')}", html=True)
        self.assertContains(response, f"Date joined: {user.date_joined.strftime('%B %d, %Y')}", html=True)

    def test_user_detail_superuser_and_not_active_users_returns_404(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        response = self.client.get(f"/accounts/users/{user.username}")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user.is_superuser = True
        user.save()
        response = self.client.get(f"/accounts/users/{user.username}")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        user.is_superuser = False
        user.is_active = False
        user.save()
        response = self.client.get(f"/accounts/users/{user.username}")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_detail_username_slug_url(self):
        user = get_user_model().objects.create_user(
            username="Test-1@.+_-", email="test@test.com", password="Test12345"
        )
        response = self.client.get(f"/accounts/users/{user.id}")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.client.get(f"/accounts/users/{user.username}")
        self.assertEqual(response.status_code, HTTPStatus.OK)

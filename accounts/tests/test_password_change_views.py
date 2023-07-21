from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase


class PasswordChangeViewsTests(TestCase):
    def test_password_change_not_authenticated_redirect_to_login(self):
        response = self.client.get("/accounts/password_change/", follow=True)
        self.assertRedirects(
            response,
            "/accounts/login/?next=/accounts/password_change/",
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_get_password_change(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.login(username="Test", password="Test12345")
        response = self.client.get("/accounts/password_change/")
        self.assertContains(response, "<h1>Change password</h1>", html=True, status_code=HTTPStatus.OK)

    def test_post_password_change_valid_data(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.login(username="Test", password="Test12345")
        response = self.client.post(
            "/accounts/password_change/",
            data={"old_password": "Test12345", "new_password1": "Test54321", "new_password2": "Test54321"},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_password_change_invalid_data(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.login(username="Test", password="Test12345")
        response = self.client.post(
            "/accounts/password_change/",
            data={"old_password": "", "new_password1": "Test54321", "new_password2": "Test54321"},
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_change_valid_data_redirect_to_password_change_done(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.login(username="Test", password="Test12345")
        response = self.client.post(
            "/accounts/password_change/",
            data={"old_password": "Test12345", "new_password1": "Test54321", "new_password2": "Test54321"},
            follow=True,
        )
        self.assertRedirects(
            response, "/accounts/password_change/done/", status_code=HTTPStatus.FOUND, target_status_code=HTTPStatus.OK
        )

    def test_get_password_change_done(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.login(username="Test", password="Test12345")
        response = self.client.get("/accounts/password_change/done/")
        self.assertContains(response, "The password has been changed!", html=True, status_code=HTTPStatus.OK)

    def test_password_change_integration_test(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.login(username="Test", password="Test12345")
        self.client.post(
            "/accounts/password_change/",
            data={"old_password": "Test12345", "new_password1": "Test54321", "new_password2": "Test54321"},
            follow=True,
        )
        self.client.logout()
        login = self.client.login(username="Test", password="Test12345")
        self.assertFalse(login)
        login = self.client.login(username="Test", password="Test54321")
        self.assertTrue(login)

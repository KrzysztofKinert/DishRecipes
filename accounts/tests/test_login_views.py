from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase


class LoginLogoutViewsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user(username="test", email="test@test.com", password="1234")

    def test_get_login(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "<h1>Log in</h1>", html=True)

    def test_post_login_valid_data(self):
        response = self.client.post("/accounts/login/", data={"username": "test", "password": "1234"})
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_login_invalid_data(self):
        response = self.client.post("/accounts/login/", data={"username": "test2", "password": "4321"})
        self.assertNotEqual(response.status_code, HTTPStatus.FOUND)

    def test_login_valid_data(self):
        response = self.client.post("/accounts/login/", data={"username": "test", "password": "1234"}, follow=True)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_invalid_data(self):
        response = self.client.post("/accounts/login/", data={"username": "test", "password": "4321"}, follow=True)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_get_logout(self):
        response = self.client.get("/accounts/logout/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "<h1>Logged out!</h1>", html=True)

    def test_logout(self):
        login = self.client.login(username="test", password="1234")
        self.assertTrue(login)
        response = self.client.request()
        self.assertTrue(response.context["user"].is_authenticated)
        response = self.client.post("/accounts/logout/", follow=True)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_login_next_not_authenticated(self):
        response = self.client.get("/accounts/login/?next=/accounts/password_change/")
        self.assertContains(response, "Please login to see this page.", status_code=HTTPStatus.OK)

    def test_login_next_authenticated(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        self.client.login(username="Test", password="Test12345")
        response = self.client.get("/accounts/login/?next=/accounts/password_change/")
        self.assertContains(response, "Your account doesn't have access to this page.", status_code=HTTPStatus.OK)

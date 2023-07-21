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

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


class SignupViewTests(TestCase):
    def test_get_signup(self):
        response = self.client.get("/accounts/signup")
        self.assertContains(response, "<h1>Sign up</h1>", html=True, status_code=HTTPStatus.OK)

    def test_post_signup_valid_data(self):
        response = self.client.post(
            "/accounts/signup",
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"},
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_signup_invalid_data(self):
        response = self.client.post(
            "/accounts/signup",
            data={"username": "", "email": "", "password1": "", "password2": ""},
        )
        self.assertNotEqual(response.status_code, HTTPStatus.FOUND)

    def test_signup_valid_data(self):
        response = self.client.post(
            "/accounts/signup",
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertTrue(response.context["user"].is_authenticated)

    def test_signup_invalid_data(self):
        response = self.client.post(
            "/accounts/signup",
            data={"username": "", "email": "", "password1": "", "password2": ""},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(get_user_model().objects.count(), 0)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_signup_fails_if_username_exists(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        response = self.client.post(
            "/accounts/signup",
            data={"username": "Test", "email": "Test2@test.com", "password1": "Test12345", "password2": "Test12345"},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(get_user_model().objects.count(), 2)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_signup_fails_if_email_exists(self):
        get_user_model().objects.create_user(username="Test", email="Test@test.com", password="Test12345")
        response = self.client.post(
            "/accounts/signup",
            data={"username": "Test2", "email": "Test@test.com", "password1": "Test12345", "password2": "Test12345"},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotEqual(get_user_model().objects.count(), 2)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_signup_success_shows_success_message(self):
        response = self.client.post(
            "/accounts/signup",
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"},
            follow=True,
        )
        self.assertContains(response, '<ul class="messages">', status_code=HTTPStatus.OK)
        self.assertContains(response, "Registration successful", status_code=HTTPStatus.OK)

    def test_signup_success_redirects_to_success_url(self):
        response = self.client.post(
            "/accounts/signup",
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"},
            follow=True,
        )
        self.assertRedirects(response, '/accounts/login/', status_code=HTTPStatus.FOUND)
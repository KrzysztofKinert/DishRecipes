from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserDetailViewTests(TestCase):
    def test_get_user_deactivate_not_authenticated_redirects_to_login_with_next(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        response = self.client.get(reverse("user-deactivate", kwargs={"slug": user.username}))
        self.assertRedirects(
            response,
            f"/accounts/login/?next=" + reverse("user-deactivate", kwargs={"slug": user.username}),
            HTTPStatus.FOUND,
            HTTPStatus.OK,
        )

    def test_get_user_deactivate_authenticated_as_another_user(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        user2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        response = self.client.get(reverse("user-deactivate", kwargs={"slug": user2.username}))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_user_deactivate_authenticated(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        response = self.client.get(reverse("user-deactivate", kwargs={"slug": user.username}))
        self.assertTemplateUsed(response, "users/user_deactivate_form.html")
        self.assertContains(
            response, "<h1>Confirm credentials to deactivate account</h1>", html=True, status_code=HTTPStatus.OK
        )

    def test_post_user_deactivate_valid_data(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        data = {"username": user.username, "password": "Test12345"}
        url = reverse("user-deactivate", kwargs={"slug": user.username})
        response = self.client.post(url, data, follow=True)
        user = get_user_model().objects.all()[0]
        self.assertFalse(user.is_active)
        self.assertRedirects(
            response,
            reverse("users"),
            HTTPStatus.FOUND,
            HTTPStatus.OK,
        )
        self.assertContains(response, '<ul class="messages">', status_code=HTTPStatus.OK)
        self.assertContains(
            response,
            "Account successfully deactivated.",
            status_code=HTTPStatus.OK,
        )

    def test_post_user_deactivate_invalid_data(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        data = {"username": user.username, "password": "Test54321"}
        url = reverse("user-deactivate", kwargs={"slug": user.username})
        response = self.client.post(url, data, follow=True)
        user = get_user_model().objects.all()[0]
        self.assertTrue(user.is_active)
        self.assertContains(
            response,
            "Please enter a correct username and password",
            status_code=HTTPStatus.OK,
        )
        data = {"username": "Test2", "password": "Test12345"}
        url = reverse("user-deactivate", kwargs={"slug": user.username})
        response = self.client.post(url, data, follow=True)
        user = get_user_model().objects.all()[0]
        self.assertTrue(user.is_active)
        self.assertContains(
            response,
            "Please enter a correct username and password",
            status_code=HTTPStatus.OK,
        )

    def test_post_user_deactivate_valid_data_for_another_user(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        user2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        data = {"username": user2.username, "password": "Test12345"}
        url = reverse("user-deactivate", kwargs={"slug": user.username})
        response = self.client.post(url, data, follow=True)
        user = get_user_model().objects.all()[0]
        user2 = get_user_model().objects.all()[1]
        self.assertTrue(user.is_active)
        self.assertTrue(user2.is_active)
        self.assertContains(
            response,
            "Please enter a correct username and password",
            status_code=HTTPStatus.OK,
        )

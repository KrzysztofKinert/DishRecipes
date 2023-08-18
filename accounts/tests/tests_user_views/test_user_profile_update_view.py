from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from os import remove

from django.urls import reverse, reverse_lazy


class UserProfileUpdateViewTests(TestCase):
    def test_get_user_profile_update_not_authenticated_redirects_to_login_with_next(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        response = self.client.get(reverse("user-profile-update", kwargs={"slug": user.username}))
        self.assertRedirects(
            response,
            reverse("login") + "?next=" + reverse("user-profile-update", kwargs={"slug": user.username}),
            HTTPStatus.FOUND,
            HTTPStatus.OK,
        )

    def test_get_user_profile_update_update_authenticated(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        response = self.client.get(reverse("user-profile-update", kwargs={"slug": user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "users/profile_form.html")
        self.assertContains(
            response,
            '<img class="img-fluid my-1" src="/media/images/default.jpg" alt="Current image" height="400" width="800">',
            html=True,
        )

    def test_post_user_profile_update_no_image(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        response = self.client.post(
            reverse("user-profile-update", kwargs={"slug": user.username}),
            data={
                "profile_bio": "Test bio",
                "profile_image":""
            }
        )
        self.assertRedirects(
            response,
            reverse("user-detail", kwargs={"slug": user.username}),
            HTTPStatus.FOUND,
            HTTPStatus.OK,
        )
        user = get_user_model().objects.all()[0]
        self.assertEqual(user.profile_image.name, "images/default.jpg")
        self.assertEqual(user.profile_bio, "Test bio")

    def test_post_user_profile_update_valid_data(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        image = SimpleUploadedFile(
            name="test.gif",
            content=(
                b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
                b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
                b"\x02\x4c\x01\x00\x3b"
            ),
            content_type="image/gif",
        )
        data = {"profile_bio": "Test bio", "profile_image": image}
        url = reverse_lazy("user-profile-update", kwargs={"slug": user.username})
        response = self.client.post(url, data)
        user = get_user_model().objects.all()[0]
        self.assertRedirects(
            response,
            f"/accounts/users/{user.username}/",
            HTTPStatus.FOUND,
            HTTPStatus.OK,
        )
        self.assertEqual(user.profile_image.name, "images/test.gif")
        self.assertEqual(user.profile_bio, "Test bio")
        remove("uploads/images/test.gif")

    def test_post_user_profile_update_clear_image(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        data = {"profile_image-clear": "on"}
        url = reverse_lazy("user-profile-update", kwargs={"slug": user.username})
        response = self.client.post(url, data)
        self.assertRedirects(
            response,
            f"/accounts/users/{user.username}/",
            HTTPStatus.FOUND,
            HTTPStatus.OK,
        )
        user = get_user_model().objects.all()[0]
        self.assertFalse(user.profile_image)

    def test_post_user_profile_update_invalid_data(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        file = SimpleUploadedFile(
            name="test.txt",
            content=(b"\x74\x78\x74"),
            content_type="text/plain",
        )
        data = {"profile_image": file}
        url = reverse_lazy("user-profile-update", kwargs={"slug": user.username})
        response = self.client.post(url, data)
        user = get_user_model().objects.all()[0]
        self.assertEqual(user.profile_image.name, "images/default.jpg")
        self.assertContains(response, '<ul class="messages">', status_code=HTTPStatus.OK)
        self.assertContains(
            response,
            "Upload a valid image. The file you uploaded was either not an image or a corrupted image.",
            status_code=HTTPStatus.OK,
        )

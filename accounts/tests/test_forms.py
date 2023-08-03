from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import CustomUserCreationForm, UserProfileImageForm


class CustomUserCreationFormTests(TestCase):
    def test_empty_form(self):
        form = CustomUserCreationForm()
        self.assertIn("username", form.fields)
        self.assertIn("email", form.fields)
        self.assertIn("password1", form.fields)
        self.assertIn("password2", form.fields)

    def test_form_valid_if_data_valid(self):
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_if_data_invalid(self):
        form = CustomUserCreationForm(
            data={"username": "", "email": "test@test.com", "password1": "Test", "password2": "Test"}
        )
        self.assertFalse(form.is_valid())

    def test_form_usernamex_validation(self):
        form = CustomUserCreationForm(
            data={"username": "", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertFalse(form.is_valid())
        form = CustomUserCreationForm(
            data={"username": "/", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertFalse(form.is_valid())
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertTrue(form.is_valid())

    def test_form_email_validation(self):
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertFalse(form.is_valid())
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test@com", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertFalse(form.is_valid())
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "@test.com", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertFalse(form.is_valid())
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertTrue(form.is_valid())

    def test_form_password_validation(self):
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test@test.com", "password1": "test", "password2": "test"}
        )
        self.assertFalse(form.is_valid())
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "test"}
        )
        self.assertFalse(form.is_valid())
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test@test.com", "password1": "test", "password2": "Test12345"}
        )
        self.assertFalse(form.is_valid())
        form = CustomUserCreationForm(
            data={"username": "Test", "email": "test@test.com", "password1": "Test12345", "password2": "Test12345"}
        )
        self.assertTrue(form.is_valid())

    def test_can_save_valid_form_from_post(self):
        request = HttpRequest()
        request.POST = {
            "username": "Test",
            "email": "test@test.com",
            "password1": "Test12345",
            "password2": "Test12345",
        }
        form = CustomUserCreationForm(request.POST)
        form.save()
        self.assertEqual(get_user_model().objects.count(), 1)

    def test_cannot_save_invalid_form_from_post(self):
        request = HttpRequest()
        request.POST = {"username": "", "email": "test", "password1": "test", "password2": "test"}
        form = CustomUserCreationForm(request.POST)
        with self.assertRaises(ValueError):
            form.save()

    def test_no_profile_image_field_in_form(self):
        form = CustomUserCreationForm()
        self.assertNotIn("profile_image", form.fields)


class UserProfileImageFormTests(TestCase):
    def test_empty_form(self):
        form = UserProfileImageForm()
        self.assertFalse(form.is_valid())
        self.assertIn("profile_image", form.fields)
        self.assertNotIn("username", form.fields)
        self.assertNotIn("email", form.fields)
        self.assertNotIn("password1", form.fields)
        self.assertNotIn("password2", form.fields)
        self.assertInHTML('<input type="file" name="profile_image" accept="image/*" id="id_profile_image">', str(form))

    def test_form_from_instance(self):
        user = get_user_model().objects.create_user(username="username", email="test@test.com", password="1234")
        request = HttpRequest()
        request.POST = {
            "username": "Test",
            "email": "test@test.com",
            "password1": "Test12345",
            "password2": "Test12345",
        }
        form = UserProfileImageForm(instance=user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.username, "username")
        self.assertEqual(form.instance.email, "test@test.com")
        self.assertEqual(form.instance.profile_image, "images/default.jpg")

    def test_form_from_post(self):
        user = get_user_model().objects.create_user(username="username", email="test@test.com", password="1234")
        request = HttpRequest()
        request.FILES = {
            "profile_image": SimpleUploadedFile(
                name="test.gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
                    b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
                    b"\x02\x4c\x01\x00\x3b"
                ),
                content_type="image/gif",
            )
        }
        form = UserProfileImageForm(files=request.FILES, instance=user)
        self.assertTrue(form.files["profile_image"].name == "test.gif")
        self.assertTrue(form.is_valid())
        request.FILES = {
            "profile_image": SimpleUploadedFile(
                name="test.txt",
                content=(
                    b"\x74\x78\x74"
                ),
                content_type="text/plain",
            )
        }
        form = UserProfileImageForm(files=request.FILES, instance=user)
        self.assertTrue(form.files["profile_image"].name == "test.txt")
        self.assertFalse(form.is_valid())
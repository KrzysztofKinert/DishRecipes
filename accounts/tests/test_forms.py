from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from ..forms import CustomUserCreationForm


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
        form = CustomUserCreationForm(data={"username": "", "email": "test@test.com", "password1": "Test", "password2": "Test"})
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
        form = CustomUserCreationForm(data={"username": "Test", "email": "test", "password1": "Test12345", "password2": "Test12345"})
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
        form = CustomUserCreationForm(data={"username": "Test", "email": "test@test.com", "password1": "test", "password2": "test"})
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


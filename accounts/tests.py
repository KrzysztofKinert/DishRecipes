from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase


class ModelsTests(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(username="test", email="test@test.com", password="1234")
        self.assertIsInstance(user, get_user_model())
        self.assertEqual(user.username, "test")
        self.assertEqual(user.email, "test@test.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        with self.assertRaises(TypeError):
            User.objects.create_user(username="test")
        with self.assertRaises(TypeError):
            User.objects.create_user(email="test@test.com")
        with self.assertRaises(ValueError):
            User.objects.create_user(username="test", email="")
        with self.assertRaises(ValueError):
            User.objects.create_user(username="", email="test@test.com")

    def test_create_user_username_is_unique(self):
        User = get_user_model()
        user = User.objects.create_user(username="test", email="test@test.com", password="1234")
        self.assertIsInstance(user, get_user_model())

        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="test", email="test_unique@test.com", password="1234")

    def test_create_user_email_is_unique(self):
        User = get_user_model()
        user = User.objects.create_user(username="test", email="test@test.com", password="1234")
        self.assertIsInstance(user, get_user_model())

        with self.assertRaises(IntegrityError):
            User.objects.create_user(username="test_unique", email="test@test.com", password="1234")

    def test_create_superuser(self):
        User = get_user_model()
        admin_user = User.objects.create_superuser(username="superuser", email="super@user.com", password="foo")
        self.assertIsInstance(admin_user, get_user_model())
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="superuser", email="super@user.com", password="foo", is_superuser=False
            )

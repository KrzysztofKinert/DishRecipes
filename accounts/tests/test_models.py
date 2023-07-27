from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from os import path, remove

class CustomUserTests(TestCase):
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
        admin_user = User.objects.create_superuser(username="superuser", email="super@user.com", password="1234")
        self.assertIsInstance(admin_user, get_user_model())
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username="superuser", email="super@user.com", password="1234", is_superuser=False
            )

    def test_user_object_name_is_username(self):
        User = get_user_model()
        user = User.objects.create_superuser(username="username", email="test@test.com", password="1234")
        expected_object_name = f"{user.username}"
        self.assertEqual(str(user), expected_object_name)

    def test_default_profile_image(self):
        default_image_name = "default.jpg"
        user = get_user_model().objects.create_superuser(username="username", email="test@test.com", password="1234")
        self.assertEqual(user.profile_image.name, "images/" + default_image_name)
        self.assertEqual(user.profile_image.url, "/media/images/" + default_image_name)

    def test_profile_image_upload(self):
        test_image_name = "test.gif"
        test_image_content = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        user = get_user_model().objects.create_superuser(username="username", email="test@test.com", password="1234")
        user.profile_image = SimpleUploadedFile(
            name=test_image_name, content=test_image_content, content_type="image/gif"
        )
        user.save()
        self.assertEqual(user.profile_image.name, "images/" + test_image_name)
        self.assertEqual(user.profile_image.url, "/media/images/" + test_image_name)
        self.assertTrue(path.isfile("uploads/images/" + test_image_name))
        remove("uploads/images/" + test_image_name)
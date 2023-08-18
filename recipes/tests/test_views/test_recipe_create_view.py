from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from os import remove

from recipes.models import Recipe


class RecipeCreateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")

    def test_get_recipe_create_not_authenticated_redirects_to_login_with_next(self):
        response = self.client.get(reverse("recipe-create"))
        self.assertRedirects(
            response,
            reverse("login") + "?next=/recipes/new/",
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_get_recipe_create_authenticated(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.get(reverse("recipe-create"))
        self.assertTemplateUsed(response, "recipes/recipe_create.html")
        self.assertContains(response, "<h1>Write your recipe</h1>", html=True, status_code=HTTPStatus.OK)

    def test_post_recipe_create_not_authenticated_redirects_to_login_with_next(self):
        response = self.client.post(
            reverse("recipe-create"),
            data={
                "title": "Test",
                "excerpt": "test excerpt",
                "ingredients": "test ingredients",
                "preparation": "test preparation",
                "serving": "test serving",
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("login") + "?next=/recipes/new/",
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_post_recipe_create_authenticated_valid_data(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-create"),
            data={
                "image": SimpleUploadedFile(
                    name="test.gif",
                    content=(
                        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
                        b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
                        b"\x02\x4c\x01\x00\x3b"
                    ),
                    content_type="image/gif",
                ),
                "title": "Test",
                "excerpt": "test excerpt",
                "ingredients": "test ingredients",
                "preparation": "test preparation",
                "serving": "test serving",
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("recipe-detail", kwargs={"slug": "test"}),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )
        recipe = Recipe.objects.get(pk=1)
        self.assertEqual(recipe.author, author)
        self.assertEqual(recipe.image, "images/test.gif")
        self.assertEqual(recipe.title, "Test")
        self.assertEqual(recipe.excerpt, "test excerpt")
        self.assertEqual(recipe.ingredients, "test ingredients")
        self.assertEqual(recipe.preparation, "test preparation")
        self.assertEqual(recipe.serving, "test serving")
        remove("uploads/images/test.gif")

    def test_post_recipe_create_authenticated_invalid_data(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-create"),
            data={
                "title": "",
                "excerpt": "",
                "ingredients": "",
                "preparation": "",
                "serving": "",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Recipe.objects.count(), 0)

    def test_post_recipe_create_authenticated_invalid_image_file(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-create"),
            data={
                "image": SimpleUploadedFile(
                    name="test.txt",
                    content=(b"\x74\x78\x74"),
                    content_type="text/plain",
                ),
                "title": "Test",
                "excerpt": "Test",
                "ingredients": "Test",
                "preparation": "Test",
                "serving": "Test",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Recipe.objects.count(), 0)

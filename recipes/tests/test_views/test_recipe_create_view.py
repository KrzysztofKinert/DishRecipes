from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

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
            reverse("recipe-detail", kwargs={"slug":"test"}),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )
        recipe = Recipe.objects.get(pk=1)
        self.assertEqual(recipe.author, author)
        self.assertEqual(recipe.title, "Test")
        self.assertEqual(recipe.excerpt, "test excerpt")
        self.assertEqual(recipe.ingredients, "test ingredients")
        self.assertEqual(recipe.preparation, "test preparation")
        self.assertEqual(recipe.serving, "test serving")

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
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Recipe.objects.count(), 0)
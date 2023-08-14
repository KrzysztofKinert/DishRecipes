from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model

from recipes.models import Recipe


class RecipeDetailTests(TestCase):
    def test_get_recipe_detail(self):
        recipe = Recipe.objects.create(
            title="test",
        )
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")
        self.assertContains(response, f'<h1 class="px-5">test</h1>', html=True, status_code=HTTPStatus.OK)

    def test_recipe_detail_contains_recipe(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        recipe = Recipe.objects.create(
            author=user,
            title="test recipe",
            excerpt="test",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertContains(response, f"{recipe.title}", html=True, status_code=HTTPStatus.OK)
        self.assertContains(response, f"Written: {recipe.created_date.strftime('%b %d, %Y')}", html=True)
        self.assertContains(response, f"<p>{recipe.ingredients}</p>", html=True)
        self.assertContains(response, f"<p>{recipe.preparation}</p>", html=True)
        self.assertContains(response, f"<p>{recipe.serving}</p>", html=True)
        
    def test_recipe_detail_username_slug_url(self):
        user = get_user_model().objects.create_user(
            username="Test-1@.+_-", email="test@test.com", password="Test12345"
        )
        recipe = Recipe.objects.create(
            author=user,
            title="test recipe",
            excerpt="test",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        response = self.client.get(f"/recipes/{recipe.id}/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.client.get(f"/recipes/{recipe.slug}/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_recipe_detail_settings_only_visible_to_authenticated_author(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        user2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        recipe = Recipe.objects.create(
            author=user,
            title="test recipe",
            excerpt="test",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertNotContains(response, "Open recipe settings", html=True, status_code=HTTPStatus.OK)
        self.client.login(username=user2.username, password="Test12345")
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertNotContains(response, "Open recipe settings", html=True, status_code=HTTPStatus.OK)
        self.client.login(username=user.username, password="Test12345")
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertContains(response, "Open recipe settings", html=True, status_code=HTTPStatus.OK)
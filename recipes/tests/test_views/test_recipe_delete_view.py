from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from recipes.models import Recipe


class RecipeUpdateTests(TestCase):
    def setUp(self):
        author = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        Recipe.objects.create(
            author=author,
            title="test",
            excerpt="test excerpt",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )

    def test_get_recipe_delete_not_authenticated_redirects_to_login_with_next(self):
        response = self.client.get(reverse("recipe-delete", kwargs={"slug": "test"}))
        self.assertRedirects(
            response,
            reverse("login") + f'?next={reverse("recipe-delete", kwargs={"slug":"test"})}',
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_get_recipe_delete_authenticated_as_another_user(self):
        author2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        self.client.login(username=author2.username, password="Test12345")
        response = self.client.get(reverse("recipe-delete", kwargs={"slug": "test"}))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_recipe_delete_authenticated(self):
        author = get_user_model().objects.get(pk=1)
        recipe = Recipe.objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.get(reverse("recipe-delete", kwargs={"slug": "test"}))
        self.assertTemplateUsed(response, "recipes/recipe_delete.html")
        self.assertContains(
            response,
            f'<h3 class="py-2">Are you sure you want to delete recipe { recipe }?</h3>',
            html=True,
            status_code=HTTPStatus.OK,
        )

    def test_post_recipe_delete_not_authenticated_redirects_to_login_with_next(self):
        response = self.client.post(
            reverse("recipe-delete", kwargs={"slug": "test"}),
        )
        self.assertRedirects(
            response,
            reverse("login") + f'?next={reverse("recipe-delete", kwargs={"slug":"test"})}',
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_post_recipe_delete_authenticated_as_another_user(self):
        author2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        self.client.login(username=author2.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-delete", kwargs={"slug": "test"}),
            data={},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_post_recipe_delete_authenticated_valid_data(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-delete", kwargs={"slug": "test"}),
            data={},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("recipe-list"),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )
        self.assertEqual(Recipe.objects.count(), 0)

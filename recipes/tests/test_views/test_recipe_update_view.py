from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from os import remove

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

    def test_get_recipe_update_not_authenticated_redirects_to_login_with_next(self):
        response = self.client.get(reverse("recipe-update", kwargs={"slug": "test"}))
        self.assertRedirects(
            response,
            reverse("login") + f'?next={reverse("recipe-update", kwargs={"slug":"test"})}',
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_get_recipe_update_authenticated_as_another_user(self):
        author2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        self.client.login(username=author2.username, password="Test12345")
        response = self.client.get(reverse("recipe-update", kwargs={"slug": "test"}))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_recipe_update_authenticated(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.get(reverse("recipe-update", kwargs={"slug": "test"}))
        self.assertTemplateUsed(response, "recipes/recipe_update.html")
        self.assertContains(response, "<h1>Edit your recipe</h1>", html=True, status_code=HTTPStatus.OK)
        self.assertContains(
            response,
            '<img class="img-fluid my-1" src="/media/images/default.jpg" alt="Current image" height="200" width="400">',
            html=True,
        )

    def test_post_recipe_update_not_authenticated_redirects_to_login_with_next(self):
        response = self.client.post(
            reverse("recipe-update", kwargs={"slug": "test"}),
            data={
                "title": "test",
                "excerpt": "test excerpt",
                "ingredients": "test ingredients",
                "preparation": "test preparation",
                "serving": "test serving",
            },
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("login") + f'?next={reverse("recipe-update", kwargs={"slug":"test"})}',
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_post_recipe_update_authenticated_as_another_user(self):
        author2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        self.client.login(username=author2.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-update", kwargs={"slug": "test"}),
            data={
                "title": "test",
                "excerpt": "test excerpt",
                "ingredients": "test ingredients",
                "preparation": "test preparation",
                "serving": "test serving",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_post_recipe_update_authenticated_valid_data(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-update", kwargs={"slug": "test"}),
            data={
                "title": "test2",
                "excerpt": "test excerpt2",
                "ingredients": "test ingredients2",
                "preparation": "test preparation2",
                "serving": "test serving2",
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
        self.assertEqual(recipe.title, "test2")
        self.assertEqual(recipe.excerpt, "test excerpt2")
        self.assertEqual(recipe.ingredients, "test ingredients2")
        self.assertEqual(recipe.preparation, "test preparation2")
        self.assertEqual(recipe.serving, "test serving2")

    def test_post_recipe_update_authenticated_invalid_data(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-update", kwargs={"slug": "test"}),
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
        recipe = Recipe.objects.get(pk=1)
        self.assertEqual(recipe.author, author)
        self.assertEqual(recipe.title, "test")
        self.assertEqual(recipe.excerpt, "test excerpt")
        self.assertEqual(recipe.ingredients, "test ingredients")
        self.assertEqual(recipe.preparation, "test preparation")
        self.assertEqual(recipe.serving, "test serving")

    def test_post_recipe_authenticated_valid_image(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-update", kwargs={"slug": "test"}),
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
                "title": "test2",
                "excerpt": "test excerpt2",
                "ingredients": "test ingredients2",
                "preparation": "test preparation2",
                "serving": "test serving2",
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
        self.assertEqual(recipe.image, "images/test.gif")
        remove("uploads/images/test.gif")

    def test_post_recipe_update_authenticated_invalid_image(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-update", kwargs={"slug": "test"}),
            data={
                "image": SimpleUploadedFile(
                    name="test.txt",
                    content=(b"\x74\x78\x74"),
                    content_type="text/plain",
                ),
                "title": "test",
                "excerpt": "test",
                "ingredients": "test",
                "preparation": "test",
                "serving": "test",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        recipe = Recipe.objects.get(pk=1)
        self.assertNotEqual(recipe.image, "images/test.txt")

    def test_post_recipe_update_authenticated_clear_image(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("recipe-update", kwargs={"slug": "test"}),
            {
                "image-clear": "on",
                "title": "test",
                "excerpt": "test",
                "ingredients": "test",
                "preparation": "test",
                "serving": "test",
            },
        )
        self.assertRedirects(
            response,
            reverse("recipe-detail", kwargs={"slug": "test"}),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )
        recipe = Recipe.objects.get(pk=1)
        self.assertFalse(recipe.image)

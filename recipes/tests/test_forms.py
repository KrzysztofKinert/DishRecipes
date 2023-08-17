from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase

from recipes.models import Recipe
from recipes.forms import RecipeForm


class CustomUserCreationFormTests(TestCase):
    def test_empty_form(self):
        form = RecipeForm()
        self.assertIn("title", form.fields)
        self.assertIn("excerpt", form.fields)
        self.assertIn("ingredients", form.fields)
        self.assertIn("preparation", form.fields)
        self.assertIn("serving", form.fields)
        self.assertNotIn("created_date", form.fields)
        self.assertNotIn("modified_date", form.fields)
        self.assertNotIn("slug", form.fields)

    def test_form_valid_if_data_valid(self):
        form = RecipeForm(
            data={
                "title": "Test",
                "excerpt": "test excerpt",
                "ingredients": "test ingredients",
                "preparation": "test preparation",
                "serving": "test serving",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_if_data_invalid(self):
        form = RecipeForm(
            data={
                "title": "",
                "excerpt": "",
                "ingredients": "",
                "preparation": "",
                "serving": "",
            }
        )
        self.assertFalse(form.is_valid())

    def test_can_save_valid_form_from_post(self):
        request = HttpRequest()
        request.POST = {
            "title": "Test",
            "excerpt": "test excerpt",
            "ingredients": "test ingredients",
            "preparation": "test preparation",
            "serving": "test serving",
        }
        form = RecipeForm(request.POST)
        form.save()
        self.assertEqual(Recipe.objects.count(), 1)

    def test_cannot_save_invalid_form_from_post(self):
        request = HttpRequest()
        request.POST = {
            "title": "",
            "excerpt": "Test",
            "ingredients": "Test",
            "preparation": "Test",
            "serving": "Test",
        }
        form = RecipeForm(request.POST)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
                "title": "Test",
                "excerpt": "",
                "ingredients": "Test",
                "preparation": "Test",
                "serving": "Test",
            }
        form = RecipeForm(request.POST)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
                "title": "Test",
                "excerpt": "Test",
                "ingredients": "",
                "preparation": "Test",
                "serving": "Test",
            }
        form = RecipeForm(request.POST)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
                "title": "Test",
                "excerpt": "Test",
                "ingredients": "Test",
                "preparation": "",
                "serving": "Test",
            }
        form = RecipeForm(request.POST)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
                "title": "Test",
                "excerpt": "Test",
                "ingredients": "Test",
                "preparation": "Test",
                "serving": "",
            }
        form = RecipeForm(request.POST)
        with self.assertRaises(ValueError):
            form.save()

    def test_form_from_instance(self):
        author = get_user_model().objects.create_user(username="username", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(
            author=author,
            title="test recipe",
            excerpt="test excerpt",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        form = RecipeForm(instance=recipe)
        self.assertTrue(form.instance)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.author, author)
        self.assertEqual(form.instance.title, "test recipe")
        self.assertEqual(form.instance.excerpt, "test excerpt")
        self.assertEqual(form.instance.ingredients, "test ingredients")
        self.assertEqual(form.instance.preparation, "test preparation")
        self.assertEqual(form.instance.serving, "test serving")
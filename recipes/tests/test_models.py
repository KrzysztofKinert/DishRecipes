from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone

from ..models import Recipe


class RecipeTests(TestCase):
    def test_create_recipe(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(
            author=user,
            title="test recipe",
            excerpt="test",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        self.assertIsInstance(recipe, Recipe)
        self.assertEqual(recipe.title, "test recipe")
        self.assertIsInstance(recipe.author, get_user_model())
        self.assertEqual(recipe.author.username, "test")
        self.assertEqual(recipe.slug, slugify(recipe.title))
        self.assertEqual(recipe.excerpt, "test")
        self.assertEqual(recipe.ingredients, "test ingredients")
        self.assertEqual(recipe.preparation, "test preparation")
        self.assertEqual(recipe.serving, "test serving")

    def test_author_set_to_null_on_user_delete(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        user.delete()
        recipe.refresh_from_db()
        self.assertIsInstance(recipe, Recipe)
        self.assertEqual(recipe.author, None)

    def test_author_recipes_returns_all_author_recipes(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        recipe2 = Recipe.objects.create(author=user, title="test recipe2", excerpt="test")
        recipe3 = Recipe.objects.create(author=user, title="test recipe3", excerpt="test")
        recipes = user.recipes.all()
        self.assertEqual(recipes.count(), 3)
        self.assertEqual(recipes[0].title, recipe.title)
        self.assertEqual(recipes[1].title, recipe2.title)
        self.assertEqual(recipes[2].title, recipe3.title)

    def test_recipe_get_absolute_url(self):
        recipe = Recipe.objects.create(author=None, title="test recipe", excerpt="test")
        self.assertEqual(recipe.get_absolute_url(), reverse("recipe-detail", kwargs={"slug": recipe.slug}))

    def test_recipe_str(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        date = timezone.now()
        self.assertEqual(recipe.__str__(), f'"test recipe", test [{date.strftime("%b %d, %Y")}]')
        user.delete()
        recipe.refresh_from_db()
        self.assertEqual(recipe.__str__(), f'"test recipe", --- [{date.strftime("%b %d, %Y")}]')

    def test_append_same_title_slug_with_int(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        recipe2 = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        self.assertEqual(recipe.slug, "test-recipe")
        self.assertEqual(recipe2.slug, "test-recipe-1")

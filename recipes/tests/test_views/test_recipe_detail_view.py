from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse

from recipes.models import Recipe

class RecipeDetailTests(TestCase):
    def test_get_recipe_detail(self):
        recipe = Recipe.objects.create(title="test")
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")
        self.assertContains(response, f"<p>{recipe.title}</p>", html=True, status_code=HTTPStatus.OK)

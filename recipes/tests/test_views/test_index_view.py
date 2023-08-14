from http import HTTPStatus
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
import datetime
from django.contrib.auth import get_user_model
from recipes.models import Recipe

class IndexViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        for i in range(1, 6):
            recipe = Recipe.objects.create(
                author=user,
                title="test recipe " + str(i),
                excerpt="test",
                ingredients="test ingredients",
                preparation="test preparation",
                serving="test serving",
            )
            recipe.created_date = recipe.created_date - datetime.timedelta(days=i*2)
            recipe.save()

    def test_get_index(self):
        recipes = list(Recipe.objects.all())
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "recipes/index.html")
        self.assertContains(response, "<h1>DishRecipes</h1>", html=True, status_code=HTTPStatus.OK)

    def test_index_shows_three_newest_recipes(self):
        response = self.client.get(reverse("index"))
        newest_recipes = Recipe.objects.all().order_by("-created_date")[:3]
        for i in range(len(newest_recipes)):
            self.assertContains(response, f'<a href={reverse("recipe-detail", kwargs={"slug": newest_recipes[i].slug})}>{newest_recipes[i].title}</a>', html=True)
            self.assertContains(response, f"<p>Written: {newest_recipes[i].created_date.strftime('%b %d, %Y')}</p>", html=True)
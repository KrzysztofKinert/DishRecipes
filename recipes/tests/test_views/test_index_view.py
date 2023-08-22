from http import HTTPStatus
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
import datetime
from django.contrib.auth import get_user_model
from django.db.models import Avg

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
            recipe.created_date = recipe.created_date - datetime.timedelta(days=i * 2)
            recipe.save()

    def test_get_index(self):
        recipes = list(Recipe.objects.all())
        response = self.client.get(reverse("index"))
        self.assertTemplateUsed(response, "recipes/index.html")
        self.assertContains(response, "<p>DishRecipes</p>", html=True, status_code=HTTPStatus.OK)

    def test_index_shows_three_newest_recipes(self):
        response = self.client.get(reverse("index"))
        newest_recipes = Recipe.objects.all().order_by("-created_date")[:3]
        for i in range(len(newest_recipes)):
            self.assertContains(
                response,
                f'<a href={reverse("recipe-detail", kwargs={"slug": newest_recipes[i].slug })}>{newest_recipes[i].title.title()}</a>',
                html=True,
            )
            if newest_recipes[i].author is not None:
                self.assertContains(
                    response,
                    f'<p><a href="{reverse("user-detail", kwargs={"slug":newest_recipes[i].author.username})}">{newest_recipes[i].author.username}</a>, {newest_recipes[i].created_date.strftime("%b %d, %Y")}</p>',
                    html=True,
                )
            else:
                self.assertContains(
                    response,
                    f'<p>{newest_recipes[i].created_date.strftime("%b %d, %Y")}</p>',
                    html=True,
                )

    def test_index_shows_three_highest_rated_recipes(self):
        response = self.client.get(reverse("index"))
        popular_recipes = Recipe.objects.annotate(avg_rating=Avg("reviews__rating")).order_by("-avg_rating")[:3]
        for i in range(len(popular_recipes)):
            self.assertContains(
                response,
                f'<a href={reverse("recipe-detail", kwargs={"slug": popular_recipes[i].slug })}>{popular_recipes[i].title.title()}</a>',
                html=True,
            )
            if popular_recipes[i].author is not None:
                self.assertContains(
                    response,
                    f'<p><a href="{reverse("user-detail", kwargs={"slug":popular_recipes[i].author.username})}">{popular_recipes[i].author.username}</a>, {popular_recipes[i].created_date.strftime("%b %d, %Y")}</p>',
                    html=True,
                )
            else:
                self.assertContains(
                    response,
                    f'<p>{popular_recipes[i].created_date.strftime("%b %d, %Y")}</p>',
                    html=True,
                )
import math
from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Avg


from recipes.models import Recipe, Review


class RecipeListViewTests(TestCase):
    num_of_recipes = 11
    paginate_by = 5
    recipe_list_template = "recipes/recipe_list.html"

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        for i in range(1, cls.num_of_recipes + 1):
            recipe = Recipe.objects.create(
                author=user,
                title="test recipe " + str(i),
                excerpt="test",
                ingredients="test ingredients",
                preparation="test preparation",
                serving="test serving",
            )
            if i%3==0:
                Review.objects.create(
                author=None,
                recipe=recipe,
                rating=1,
                content="Test 1" + str(i),
            )
            if i%2==0:
                Review.objects.create(
                author=None,
                recipe=recipe,
                rating=5,
                content="Test " + str(i),
            )
            if i%5==0:
                recipe.author=None
                recipe.save()

    def test_get_recipe_list(self):
        response = self.client.get(reverse("recipe-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, self.recipe_list_template)
        self.assertContains(response, "Recipes", html=True)

    def test_recipe_list_shows_all_recipes(self):
        response = self.client.get(reverse("recipe-list"))
        self.assertEqual(response.context_data["paginator"].count, self.num_of_recipes)

    def test_recipe_list_default_pagination(self):
        response = self.client.get(reverse("recipe-list"))
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.count, self.num_of_recipes)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_recipes / self.paginate_by))

    def test_recipe_list_set_paginate_by(self):
        response = self.client.get(reverse("recipe-list"), data={"paginate_by": "5"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 5)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_recipes / 5))
        self.assertContains(response, '<option selected value="5">5</option>', html=True)
        response = self.client.get(reverse("recipe-list"), data={"paginate_by": "10"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 10)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_recipes / 10))
        self.assertContains(response, '<option selected value="10">10</option>', html=True)
        response = self.client.get(reverse("recipe-list"), data={"paginate_by": "25"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 25)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_recipes / 25))
        self.assertContains(response, '<option selected value="25">25</option>', html=True)
        response = self.client.get(reverse("recipe-list"), data={"paginate_by": "50"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 50)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_recipes / 50))
        self.assertContains(response, '<option selected value="50">50</option>', html=True)

    def recipe_list_set_page_and_paginate_by(self, page, paginate_by):
        max_page = math.ceil(self.num_of_recipes / paginate_by)
        if paginate_by > self.num_of_recipes:
            prev_buttons_count = 0
            next_buttons_count = 0
        elif page == 1:
            prev_buttons_count = 0
            next_buttons_count = 2
        elif page == max_page:
            prev_buttons_count = 2
            next_buttons_count = 0
        else:
            prev_buttons_count = 2
            next_buttons_count = 2
        response = self.client.get(reverse("recipe-list"), data={"page": f"{page}", "paginate_by": f"{paginate_by}"})
        self.assertContains(response, f"Page {page} of {max_page}", html=True)
        self.assertContains(
            response,
            f'<button class="page-link" type="submit" name="page" value="1">&laquo; first</button>',
            prev_buttons_count,
            html=True,
        )
        self.assertContains(
            response,
            f'<button class="page-link" type="submit" name="page" value="{page-1}">previous</button>',
            prev_buttons_count,
            html=True,
        )
        self.assertContains(
            response,
            f'<button class="page-link" type="submit" name="page" value="{page+1}">next</button>',
            next_buttons_count,
            html=True,
        )
        self.assertContains(
            response,
            f'<button class="page-link" type="submit" name="page" value="{max_page}">last &raquo;</button>',
            next_buttons_count,
            html=True,
        )

    def test_recipe_list_pagination(self):
        paginate_by_list = [5, 10, 25, 50]
        for paginate_by in paginate_by_list:
            max_page = math.ceil(self.num_of_recipes / paginate_by)
            for page in range(1, max_page + 1):
                self.recipe_list_set_page_and_paginate_by(page, paginate_by)

    def test_recipe_list_set_only_paginate_by_sets_page_to_1(self):
        response = self.client.get(reverse("recipe-list"), data={"page": "2", "paginate_by": "5"})
        self.assertContains(response, f"Page 2 of {math.ceil(self.num_of_recipes / 5)}", html=True)
        response = self.client.get(reverse("recipe-list"), data={"paginate_by": "10"})
        self.assertContains(response, f"Page 1 of {math.ceil(self.num_of_recipes / 10)}", html=True)
        response = self.client.get(reverse("recipe-list"), data={"page": "2", "paginate_by": "10"})
        self.assertContains(response, f"Page 2 of {math.ceil(self.num_of_recipes / 10)}", html=True)
        response = self.client.get(reverse("recipe-list"), data={"paginate_by": "5"})
        self.assertContains(response, f"Page 1 of {math.ceil(self.num_of_recipes / 5)}", html=True)

    def test_recipe_list_shows_recipe_summary_list(self):
        response = self.client.get(reverse("recipe-list"), data={"paginate_by": "25"})
        for i in range(self.num_of_recipes):
            recipe = Recipe.objects.get(pk=i + 1)
            self.assertContains(
                response,
                f'<a href={reverse("recipe-detail", kwargs={"slug": recipe.slug})}>{recipe.title.title()}</a>',
                html=True,
            )
            if recipe.author is not None:
                self.assertContains(
                    response,
                    f'<p><a href="{reverse("user-detail", kwargs={"slug":recipe.author.username})}">{recipe.author.username}</a>, {recipe.created_date.strftime("%b %d, %Y")}</p>',
                    html=True,
                )
            else:
                self.assertContains(
                    response,
                    f'<p>{recipe.created_date.strftime("%b %d, %Y")}</p>',
                    html=True,
                )
            avg_rating = recipe.get_avg_rating()
            self.assertContains(
                response,
                f'<p>Rating: {avg_rating}/5</p>',
                html=True,
            )
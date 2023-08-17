import math
from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from recipes.models import Recipe


class UserRecipeListViewTests(TestCase):
    num_of_user_recipes = 11
    paginate_by = 5
    user_recipe_list_template = "users/user_recipe_list.html"

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(username=f"Test", email=f"test@test.com", password="Test12345")
        user2 = get_user_model().objects.create_user(username=f"Test2", email=f"test2@test.com", password="Test12345")
        for i in range(1, cls.num_of_user_recipes + 1):
            Recipe.objects.create(
                author=user,
                title="test recipe " + str(i),
                excerpt="test",
                ingredients="test ingredients",
                preparation="test preparation",
                serving="test serving",
            )
        for i in range(1, 3):
            Recipe.objects.create(
                author=user2,
                title="test recipe " + str(i),
                excerpt="test",
                ingredients="test ingredients",
                preparation="test preparation",
                serving="test serving",
            )

    def test_get_user_recipe_list(self):
        user = get_user_model().objects.get(pk=1)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}))
        self.assertTemplateUsed(response, self.user_recipe_list_template)
        self.assertContains(response, f"{user.username}'s Recipes", html=True, status_code=HTTPStatus.OK)

    def test_user_recipe_list_superuser_and_not_active_users_returns_404(self):
        user = get_user_model().objects.get(pk=1)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        user.is_superuser = True
        user.save()
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        user.is_superuser = False
        user.is_active = False
        user.save()
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_user_recipe_list_shows_all_user_recipes(self):
        user = get_user_model().objects.get(pk=1)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}))
        self.assertEqual(response.context_data["paginator"].count, self.num_of_user_recipes)

    def test_user_recipe_list_default_pagination(self):
        user = get_user_model().objects.get(pk=1)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}))
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.count, self.num_of_user_recipes)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_user_recipes / self.paginate_by))

    def test_user_recipe_list_set_paginate_by(self):
        user = get_user_model().objects.get(pk=1)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}), data={"paginate_by": "5"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 5)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_user_recipes / 5))
        self.assertContains(response, '<option selected value="5">5</option>', html=True)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}), data={"paginate_by": "10"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 10)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_user_recipes / 10))
        self.assertContains(response, '<option selected value="10">10</option>', html=True)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}), data={"paginate_by": "25"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 25)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_user_recipes / 25))
        self.assertContains(response, '<option selected value="25">25</option>', html=True)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}), data={"paginate_by": "50"})
        paginator = response.context_data["paginator"]
        self.assertEqual(paginator.per_page, 50)
        self.assertEqual(paginator.num_pages, math.ceil(self.num_of_user_recipes / 50))
        self.assertContains(response, '<option selected value="50">50</option>', html=True)

    def user_recipe_list_set_page_and_paginate_by(self, page, paginate_by):
        user = get_user_model().objects.get(pk=1)
        max_page = math.ceil(self.num_of_user_recipes / paginate_by)
        if paginate_by > self.num_of_user_recipes:
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
        response = self.client.get(
            reverse("user-recipes", kwargs={"slug": user.username}),
            data={"page": f"{page}", "paginate_by": f"{paginate_by}"},
        )
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

    def test_user_recipe_list_pagination(self):
        paginate_by_list = [5, 10, 25, 50]
        for paginate_by in paginate_by_list:
            max_page = math.ceil(self.num_of_user_recipes / paginate_by)
            for page in range(1, max_page + 1):
                self.user_recipe_list_set_page_and_paginate_by(page, paginate_by)

    def test_user_recipe_list_set_only_paginate_by_sets_page_to_1(self):
        user = get_user_model().objects.get(pk=1)
        response = self.client.get(
            reverse("user-recipes", kwargs={"slug": user.username}), data={"page": "2", "paginate_by": "5"}
        )
        self.assertContains(response, f"Page 2 of {math.ceil(self.num_of_user_recipes / 5)}", html=True)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}), data={"paginate_by": "10"})
        self.assertContains(response, f"Page 1 of {math.ceil(self.num_of_user_recipes / 10)}", html=True)
        response = self.client.get(
            reverse("user-recipes", kwargs={"slug": user.username}), data={"page": "2", "paginate_by": "10"}
        )
        self.assertContains(response, f"Page 2 of {math.ceil(self.num_of_user_recipes / 10)}", html=True)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}), data={"paginate_by": "5"})
        self.assertContains(response, f"Page 1 of {math.ceil(self.num_of_user_recipes / 5)}", html=True)

    def test_user_recipe_list_shows_user_recipe_summary_list(self):
        user = get_user_model().objects.get(pk=1)
        response = self.client.get(reverse("user-recipes", kwargs={"slug": user.username}), data={"paginate_by": "25"})
        for i in range(self.num_of_user_recipes):
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

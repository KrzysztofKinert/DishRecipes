from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from recipes.models import Recipe, Review


class RecipeDetailTests(TestCase):
    def test_get_recipe_detail(self):
        recipe = Recipe.objects.create(
            title="test",
        )
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")
        self.assertContains(response, f'<h1 class="px-5">Test</h1>', html=True, status_code=HTTPStatus.OK)

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
        self.assertContains(response, f"{recipe.title.title()}", html=True, status_code=HTTPStatus.OK)
        self.assertContains(
            response,
            f'<p><a href="{reverse("user-detail", kwargs={"slug":recipe.author.username})}">{recipe.author.username}</a>, {recipe.created_date.strftime("%b %d, %Y")}</p>',
            html=True,
        )
        self.assertContains(response, f"<p>{recipe.ingredients}</p>", html=True)
        self.assertContains(response, f"<p>{recipe.preparation}</p>", html=True)
        self.assertContains(response, f"<p>{recipe.serving}</p>", html=True)

    def test_recipe_detail_contains_recipe_with_no_author(self):
        recipe = Recipe.objects.create(
            author=None,
            title="test recipe",
            excerpt="test",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertContains(response, f"{recipe.title.title()}", html=True, status_code=HTTPStatus.OK)
        self.assertContains(
            response,
            f'<p>{recipe.created_date.strftime("%b %d, %Y")}</p>',
            html=True,
        )
        self.assertContains(response, f"<p>{recipe.ingredients}</p>", html=True)
        self.assertContains(response, f"<p>{recipe.preparation}</p>", html=True)
        self.assertContains(response, f"<p>{recipe.serving}</p>", html=True)

    def test_recipe_detail_username_slug_url(self):
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        recipe = Recipe.objects.create(
            author=user,
            title="test recipe",
            excerpt="test",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.id}))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
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


class RecipeDetailReviewTests(TestCase):
    def setUp(self):
        author = get_user_model().objects.create_user(username="Author", email="author@test.com", password="Test12345")
        recipe = Recipe.objects.create(
            author=author,
            title="test",
            excerpt="test excerpt",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        for i in range(5):
            user = get_user_model().objects.create_user(
                username=f"Test{i}", email=f"test{i}@test.com", password="Test12345"
            )
            Review.objects.create(
                author=user,
                recipe=recipe,
                rating=i,
                content=f"Test {i}",
            )

    def test_get_recipe_reviews(self):
        recipe = Recipe.objects.get(pk=1)
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertTemplateUsed(response, "recipes/recipe_detail.html")
        self.assertContains(response, f"<p>Rating: {int((1+2+3+4+5)/5)}/5</p>", html=True, status_code=HTTPStatus.OK)
        for i in range(5):
            review = Review.objects.get(pk=i + 1)
            if review.author is not None:
                self.assertContains(
                    response,
                    f'<p><a href="{reverse("user-detail", kwargs={"slug":review.author.username})}">{review.author.username}</a>, {review.created_date.strftime("%b %d, %Y")}</p>',
                    html=True,
                )
            else:
                self.assertContains(
                    response,
                    f'<p>{review.created_date.strftime("%b %d, %Y")}</p>',
                    html=True,
                )
            self.assertContains(
                response,
                f"<p>Rating: {review.rating}/5</p>",
                html=True,
            )

    def test_get_review_form_if_authenticated_and_not_recipe_author(self):
        recipe = Recipe.objects.get(pk=1)
        author = get_user_model().objects.get(pk=1)
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertNotContains(
            response,
            f'<h1>Write your review</h1>',
            html=True,
        )
        self.client.login(username=author.username, password="Test12345")
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertNotContains(
            response,
            f'<h1>Write your review</h1>',
            html=True,
        )
        self.client.login(username=user.username, password="Test12345")
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertContains(
            response,
            f'<h1>Write your review</h1>',
            html=True,
        )

    def test_post_review_form_if_authenticated_and_not_recipe_author(self):
        recipe = Recipe.objects.get(pk=1)
        author = get_user_model().objects.get(pk=1)
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        response = self.client.post(reverse("recipe-detail", kwargs={"slug": recipe.slug}), data={"rating":3,"content":"Test"})
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(reverse("recipe-detail", kwargs={"slug": recipe.slug}), data={"rating":3,"content":"Test"})
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.client.login(username=user.username, password="Test12345")
        response = self.client.post(reverse("recipe-detail", kwargs={"slug": recipe.slug}), data={"rating":3,"content":"Test"})
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_review_form_valid_data(self):
        recipe = Recipe.objects.get(pk=1)
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        response = self.client.post(reverse("recipe-detail", kwargs={"slug": recipe.slug}), data={"rating":3,"content":"Test"})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        review = recipe.get_user_review(user)
        self.assertEqual(review.author, user)
        self.assertEqual(review.recipe, recipe)
        self.assertEqual(review.rating, 3)
        self.assertEqual(review.content, "Test")

    def test_post_recipe_create_authenticated_invalid_data(self):
        recipe = Recipe.objects.get(pk=1)
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        self.client.login(username=user.username, password="Test12345")
        response = self.client.post(reverse("recipe-detail", kwargs={"slug": recipe.slug}), data={"rating":0,"content":""})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        review = recipe.get_user_review(user)
        self.assertEqual(review, None)

    def test_get_no_review_form_if_authenticated_and_not_recipe_author_and_already_reviewed(self):
        recipe = Recipe.objects.get(pk=1)
        user = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        review = Review.objects.create(
                author=user,
                recipe=recipe,
                rating=3,
                content="Test",
            )
        self.client.login(username=user.username, password="Test12345")
        response = self.client.get(reverse("recipe-detail", kwargs={"slug": recipe.slug}))
        self.assertNotContains(
            response,
            f'<h1>Write your review</h1>',
            html=True,
        )
        self.assertContains(
            response,
            f'<h4>Your review</h4>',
            html=True,
        )
        self.assertContains(
            response,
            f"<p>Rating: {review.rating}/5</p",
            html=False,
        )
        self.assertContains(
            response,
            f'<div class="px-3 pb-3">{review.content}</div>',
            html=True,
        )
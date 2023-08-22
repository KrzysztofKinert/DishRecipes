from http import HTTPStatus
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from recipes.models import Recipe, Review


class ReviewDeleteTests(TestCase):
    def setUp(self):
        author = get_user_model().objects.create_user(username="Test", email="test@test.com", password="Test12345")
        recipe = Recipe.objects.create(
            author=author,
            title="test",
            excerpt="test excerpt",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        Review.objects.create(
            author=author,
            recipe=recipe,
            rating=3,
            content="Test"
        )

    def test_get_review_delete_not_authenticated_redirects_to_login_with_next(self):
        response = self.client.get(reverse("review-delete", kwargs={"slug": "test", "pk":1}))
        self.assertRedirects(
            response,
            reverse("login") + f'?next={reverse("review-delete", kwargs={"slug": "test", "pk":1})}',
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_get_review_delete_authenticated_as_another_user(self):
        author2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        self.client.login(username=author2.username, password="Test12345")
        response = self.client.get(reverse("review-delete", kwargs={"slug": "test", "pk":1}))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_recipe_delete_authenticated(self):
        author = get_user_model().objects.get(pk=1)
        review = Review.objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.get(reverse("review-delete", kwargs={"slug": "test", "pk":1}))
        self.assertTemplateUsed(response, "recipes/review_delete.html")
        self.assertContains(
            response,
            f'<h3 class="py-2">Are you sure you want to delete review { review }?</h3>',
            html=True,
            status_code=HTTPStatus.OK,
        )

    def test_post_recipe_delete_not_authenticated_redirects_to_login_with_next(self):
        response = self.client.post(
            reverse("review-delete", kwargs={"slug": "test", "pk":1}),
        )
        self.assertRedirects(
            response,
            reverse("login") + f'?next={reverse("review-delete", kwargs={"slug": "test", "pk":1})}',
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )

    def test_post_recipe_delete_authenticated_as_another_user(self):
        author2 = get_user_model().objects.create_user(username="Test2", email="test2@test.com", password="Test12345")
        self.client.login(username=author2.username, password="Test12345")
        response = self.client.post(
            reverse("review-delete", kwargs={"slug": "test", "pk":1}),
            data={},
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_post_recipe_delete_authenticated_valid_data(self):
        author = get_user_model().objects.get(pk=1)
        self.client.login(username=author.username, password="Test12345")
        response = self.client.post(
            reverse("review-delete", kwargs={"slug": "test", "pk":1}),
            data={},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("recipe-detail", kwargs={"slug":"test"}),
            status_code=HTTPStatus.FOUND,
            target_status_code=HTTPStatus.OK,
        )
        self.assertEqual(Review.objects.count(), 0)

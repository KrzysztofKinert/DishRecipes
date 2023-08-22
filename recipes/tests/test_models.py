from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from os import path, remove
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from recipes.models import Recipe, Review


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
        self.assertEqual(recipe.image.url, settings.MEDIA_URL + "images/default.jpg")

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

    def test_changing_title_does_not_change_slug(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe")
        self.assertEqual(recipe.slug, "test-recipe")
        recipe.title = "recipe test"
        recipe.save()
        self.assertEqual(recipe.title, "recipe test")
        self.assertEqual(recipe.slug, "test-recipe")

    def test_default_recipe_image(self):
        default_image_name = "default.jpg"
        recipe = Recipe.objects.create(author=None, title="test recipe")
        self.assertEqual(recipe.image.name, "images/" + default_image_name)
        self.assertEqual(recipe.image.url, settings.MEDIA_URL + "images/" + default_image_name)

    def test_recipe_image_url_or_default(self):
        test_image_name = "test.gif"
        default_image_name = "default.jpg"
        recipe = Recipe.objects.create(author=None, title="test recipe")
        self.assertEqual(recipe.recipe_image_url_or_default(), settings.MEDIA_URL + "images/" + default_image_name)
        recipe.image = SimpleUploadedFile(
            name=test_image_name,
            content=(
                b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
                b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
                b"\x02\x4c\x01\x00\x3b"
            ),
            content_type="image/gif",
        )
        recipe.save()
        self.assertEqual(recipe.recipe_image_url_or_default(), settings.MEDIA_URL + "images/" + test_image_name)
        recipe.image = None
        recipe.save()
        with self.assertRaises(ValueError):
            recipe.image.url
        self.assertEqual(recipe.recipe_image_url_or_default(), settings.MEDIA_URL + "images/" + default_image_name)
        remove("uploads/images/" + test_image_name)

    def test_recipe_image_upload(self):
        test_image_name = "test.gif"
        test_image_content = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
            b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
            b"\x02\x4c\x01\x00\x3b"
        )
        recipe = Recipe.objects.create(author=None, title="test recipe")
        recipe.image = SimpleUploadedFile(name=test_image_name, content=test_image_content, content_type="image/gif")
        recipe.save()
        self.assertEqual(recipe.image.name, "images/" + test_image_name)
        self.assertEqual(recipe.image.url, "/media/images/" + test_image_name)
        self.assertTrue(path.isfile("uploads/images/" + test_image_name))
        remove("uploads/images/" + test_image_name)

    def test_get_avg_rating(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        user2 = get_user_model().objects.create_user(username="test2", email="test2@test.com", password="1234")
        user3 = get_user_model().objects.create_user(username="test3", email="test3@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        self.assertEqual(recipe.get_avg_rating(), "-")
        review = Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        review2 = Review.objects.create(author=user2, recipe=recipe, rating=3, content="test")
        review3 = Review.objects.create(author=user3, recipe=recipe, rating=3, content="test")
        self.assertEqual(recipe.get_avg_rating(), (review.rating + review2.rating + review3.rating)/3)

    def test_get_user_review(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        review = Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        self.assertEqual(recipe.get_user_review(user), review)

class ReviewTests(TestCase):
    def test_create_review(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(
            author=user,
            title="test recipe",
            excerpt="test",
            ingredients="test ingredients",
            preparation="test preparation",
            serving="test serving",
        )
        review = Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        self.assertIsInstance(review, Review)
        self.assertIsInstance(review.author, get_user_model())
        self.assertIsInstance(review.recipe, Recipe)
        self.assertEqual(review.author.username, "test")
        self.assertEqual(review.recipe.title, "test recipe")
        self.assertEqual(review.rating, 3)
        self.assertEqual(review.content, "test")
        
    def test_author_set_to_null_on_user_delete(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        review = Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        user.delete()
        review.refresh_from_db()
        self.assertIsInstance(review, Review)
        self.assertEqual(review.author, None)

    def test_review_deleted_on_recipe_delete(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        review = Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        recipe.delete()
        with self.assertRaises(ObjectDoesNotExist):
            review.refresh_from_db()

    def test_author_reviews_returns_all_author_reviews(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        review = Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        recipe2 = Recipe.objects.create(author=user, title="test recipe2", excerpt="test")
        review2 = Review.objects.create(author=user, recipe=recipe2, rating=3, content="test")
        recipe3 = Recipe.objects.create(author=user, title="test recipe3", excerpt="test")
        review3 = Review.objects.create(author=user, recipe=recipe3, rating=3, content="test")
        reviews = user.recipes.all()
        self.assertEqual(reviews.count(), 3)
        self.assertEqual(reviews[0].author, review.author)
        self.assertEqual(reviews[1].author, review2.author)
        self.assertEqual(reviews[2].author, review3.author)

    def test_recipe_reviews_returns_all_recipe_reviews(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        user2 = get_user_model().objects.create_user(username="test2", email="test2@test.com", password="1234")
        user3 = get_user_model().objects.create_user(username="test3", email="test3@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        review = Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        review2 = Review.objects.create(author=user2, recipe=recipe, rating=3, content="test")
        review3 = Review.objects.create(author=user3, recipe=recipe, rating=3, content="test")
        reviews = recipe.reviews.all()
        self.assertEqual(reviews.count(), 3)
        self.assertEqual(reviews[0].recipe, review.recipe)
        self.assertEqual(reviews[1].recipe, review2.recipe)
        self.assertEqual(reviews[2].recipe, review3.recipe)

    def test_review_str(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        review = Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        date = timezone.now()
        self.assertEqual(review.__str__(), f'"test recipe" - 3/5, test [{date.strftime("%b %d, %Y")}]')
        user.delete()
        review.refresh_from_db()
        self.assertEqual(review.__str__(), f'"test recipe" - 3/5, --- [{date.strftime("%b %d, %Y")}]')
    
    def test_review_unique_author_recipe(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
        with self.assertRaises(IntegrityError):
            Review.objects.create(author=user, recipe=recipe, rating=3, content="test")
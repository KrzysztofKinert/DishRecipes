from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from os import path, remove


from recipes.models import Recipe, Review
from recipes.forms import RecipeForm, ReviewForm


class RecipeFormTests(TestCase):
    def test_empty_form(self):
        form = RecipeForm()
        self.assertIn("image", form.fields)
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
                "image": SimpleUploadedFile(
                    name="test.gif",
                    content=(
                        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
                        b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
                        b"\x02\x4c\x01\x00\x3b"
                    ),
                    content_type="image/gif",
                ),
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
        request.FILES = {
            "image": SimpleUploadedFile(
                name="test.gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
                    b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
                    b"\x02\x4c\x01\x00\x3b"
                ),
                content_type="image/gif",
            )
        }
        form = RecipeForm(data=request.POST, files=request.FILES)
        form.save()
        recipe = Recipe.objects.get(pk=1)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(recipe.title, "Test")
        self.assertEqual(recipe.excerpt, "test excerpt")
        self.assertEqual(recipe.ingredients, "test ingredients")
        self.assertEqual(recipe.preparation, "test preparation")
        self.assertEqual(recipe.serving, "test serving")
        self.assertEqual(recipe.image, "images/test.gif")
        remove("uploads/images/test.gif")

    def test_cannot_save_invalid_form_from_post(self):
        request = HttpRequest()
        request.FILES = {
            "image": SimpleUploadedFile(
                name="test.gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
                    b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
                    b"\x02\x4c\x01\x00\x3b"
                ),
                content_type="image/gif",
            )
        }
        request.POST = {
            "title": "",
            "excerpt": "Test",
            "ingredients": "Test",
            "preparation": "Test",
            "serving": "Test",
        }
        form = RecipeForm(data=request.POST, files=request.FILES)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "title": "Test",
            "excerpt": "",
            "ingredients": "Test",
            "preparation": "Test",
            "serving": "Test",
        }
        form = RecipeForm(data=request.POST, files=request.FILES)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "title": "Test",
            "excerpt": "Test",
            "ingredients": "",
            "preparation": "Test",
            "serving": "Test",
        }
        form = RecipeForm(data=request.POST, files=request.FILES)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "title": "Test",
            "excerpt": "Test",
            "ingredients": "Test",
            "preparation": "",
            "serving": "Test",
        }
        form = RecipeForm(data=request.POST, files=request.FILES)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "title": "Test",
            "excerpt": "Test",
            "ingredients": "Test",
            "preparation": "Test",
            "serving": "",
        }
        form = RecipeForm(data=request.POST, files=request.FILES)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "title": "Test",
            "excerpt": "Test",
            "ingredients": "Test",
            "preparation": "Test",
            "serving": "Test",
        }
        request.FILES = {
            "image": SimpleUploadedFile(
                name="test.txt",
                content=(b"\x74\x78\x74"),
                content_type="text/plain",
            )
        }
        form = RecipeForm(data=request.POST, files=request.FILES)
        with self.assertRaises(ValueError):
            form.save()

    def test_form_from_instance(self):
        author = get_user_model().objects.create_user(username="username", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(
            author=author,
            image=SimpleUploadedFile(
                name="test.gif",
                content=(
                    b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04"
                    b"\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02"
                    b"\x02\x4c\x01\x00\x3b"
                ),
                content_type="image/gif",
            ),
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
        self.assertEqual(form.instance.image, "images/test.gif")
        remove("uploads/images/test.gif")


class ReviewFormTests(TestCase):
    def test_empty_form(self):
        form = ReviewForm()
        self.assertIn("rating", form.fields)
        self.assertIn("content", form.fields)
        self.assertNotIn("created_date", form.fields)
        self.assertNotIn("modified_date", form.fields)
        self.assertNotIn("author", form.fields)
        self.assertNotIn("recipe", form.fields)

    def test_form_valid_if_data_valid(self):
        form = ReviewForm(
            data={
                "rating": 3,
                "content": "Test",
            }
        )
        self.assertTrue(form.is_valid())

    def test_form_invalid_if_data_invalid(self):
        form = ReviewForm(
            data={
                "rating": 0,
                "content": "",
            }
        )
        self.assertFalse(form.is_valid())

    def test_can_save_valid_form_from_post(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        request = HttpRequest()
        request.POST = {
            "rating": 3,
            "content": "Test",
        }
        form = ReviewForm(data=request.POST)
        form.instance.author = user
        form.instance.recipe = recipe
        form.save()
        review = Review.objects.get(pk=1)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(review.rating, 3)
        self.assertEqual(review.content, "Test")

    def test_cannot_save_invalid_form_from_post(self):
        user = get_user_model().objects.create_user(username="test", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=user, title="test recipe", excerpt="test")
        request = HttpRequest()
        request.POST = {
            "rating": 0,
            "content": "Test",
        }
        form = ReviewForm(data=request.POST)
        form.instance.author = user
        form.instance.recipe = recipe
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "rating": -1,
            "content": "Test",
        }
        form = ReviewForm(data=request.POST)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "rating": 6,
            "content": "Test",
        }
        form = ReviewForm(data=request.POST)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "rating": 2.5,
            "content": "Test",
        }
        form = ReviewForm(data=request.POST)
        with self.assertRaises(ValueError):
            form.save()

        request.POST = {
            "rating": 3,
            "content": "",
        }
        form = ReviewForm(data=request.POST)
        with self.assertRaises(ValueError):
            form.save()

    def test_form_from_instance(self):
        author = get_user_model().objects.create_user(username="username", email="test@test.com", password="1234")
        recipe = Recipe.objects.create(author=author, title="test recipe", excerpt="test")
        review = Review.objects.create(author=author, recipe=recipe, rating=3, content="Test")
        form = ReviewForm(instance=review)
        self.assertTrue(form.instance)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.instance.author, author)
        self.assertEqual(form.instance.recipe, recipe)
        self.assertEqual(form.instance.rating, 3)
        self.assertEqual(form.instance.content, "Test")
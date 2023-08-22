from typing import Any, Iterable, Optional
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class Recipe(models.Model):
    author = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL, related_name="recipes")
    slug = models.SlugField(default="", blank=True, null=False, unique=True)
    title = models.CharField(max_length=100)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)
    excerpt = models.CharField(max_length=1000)
    ingredients = models.CharField(max_length=10000)
    preparation = models.CharField(max_length=10000)
    serving = models.CharField(max_length=10000)
    image = models.ImageField(
        _("recipe image"),
        max_length=200,
        upload_to="images",
        blank=True,
        default="images/default.jpg",
    )

    def get_absolute_url(self):
        return reverse("recipe-detail", args=[self.slug])

    def __str__(self):
        if self.author:
            return f'"{self.title}", {self.author.get_username()} [{self.created_date.strftime("%b %d, %Y")}]'
        else:
            return f'"{self.title}", --- [{self.created_date.strftime("%b %d, %Y")}]'

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)
            i = 1
            while Recipe.objects.filter(slug=slug).exists():
                slug = f"{slugify(self.title)}-{str(i)}"
                i += 1
            self.slug = slug
        super(Recipe, self).save(*args, **kwargs)

    def recipe_image_url_or_default(self):
        try:
            return self.image.url
        except:
            return settings.MEDIA_URL + "images/default.jpg"
        
    def get_avg_rating(self):
        avg_rating = self.reviews.aggregate(Avg("rating"))["rating__avg"]
        if avg_rating is None:
            return "-"
        else: 
            return avg_rating
        
    def get_user_review(self, user):
        return Review.objects.filter(author=user, recipe=self).first()
    


class Review(models.Model):
    author = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL, related_name="reviews")
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    content = models.CharField(max_length=2000)
    created_date = models.DateField(auto_now_add=True)
    modified_date = models.DateField(auto_now=True)

    class Meta:
        unique_together = ('author', 'recipe',)

    def __str__(self):
        if self.author:
            return f'"{self.recipe.title}" - {self.rating}/5, {self.author.get_username()} [{self.created_date.strftime("%b %d, %Y")}]'
        else:
            return f'"{self.recipe.title}" - {self.rating}/5, --- [{self.created_date.strftime("%b %d, %Y")}]'
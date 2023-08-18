from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.conf import settings


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

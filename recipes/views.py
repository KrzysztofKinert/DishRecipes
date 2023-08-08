from django.views.generic import TemplateView, DetailView

from .models import Recipe

class IndexView(TemplateView):
    template_name = "recipes/index.html"

class RecipeView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"
    slug_field = "slug"
from typing import Any, Dict
from django.http import HttpRequest, HttpResponse
from django.views.generic import TemplateView, DetailView, ListView


from django.db.models.functions import Lower

from .models import Recipe


class IndexView(ListView):
    model = Recipe
    template_name = "recipes/index.html"
    context_object_name = "newest_recipes"

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by("-created_date")[:3]
        return queryset


class RecipeView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"
    slug_field = "slug"


class RecipeList(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    paginate_by = 5

    def get_paginate_by(self, queryset):
        return self.request.GET.get("paginate_by", self.paginate_by)

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by("-created_date")
        return queryset

    def get(self, request, *args, **kwargs):
        request.GET = request.GET.copy()
        request.GET["paginate_by"] = str(self.get_paginate_by(self.get_queryset()))
        return super().get(request, *args, **kwargs)

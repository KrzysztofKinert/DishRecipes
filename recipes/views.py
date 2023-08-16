from typing import Optional
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy

from recipes.models import Recipe
from recipes.forms import RecipeForm


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


class RecipeCreate(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_create.html"

    def get_success_url(self) -> str:
        return reverse("recipe-detail", kwargs={"slug": self.object.slug})

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)


class RecipeUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_update.html"

    def get_success_url(self) -> str:
        return reverse("recipe-detail", kwargs={"slug": self.object.slug})

    def test_func(self) -> bool | None:
        recipe = self.get_object()
        return self.request.user.username == recipe.author.username


class RecipeDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Recipe
    template_name = "recipes/recipe_delete.html"

    def get_success_url(self) -> str:
        return reverse("recipe-list")

    def test_func(self) -> bool | None:
        recipe = self.get_object()
        return self.request.user.username == recipe.author.username

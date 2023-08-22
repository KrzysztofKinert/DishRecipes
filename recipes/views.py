from typing import Any, Dict, Optional
from django.db import models
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.views.generic.edit import FormMixin
from django.db.models import Avg

from recipes.models import Recipe, Review
from recipes.forms import RecipeForm, ReviewForm


class IndexView(ListView):
    model = Recipe
    template_name = "recipes/index.html"
    context_object_name = "newest_recipes"

    def get_queryset(self):
        queryset = Recipe.objects.all().order_by("-created_date")[:3]
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["popular_recipes"] = Recipe.objects.annotate(avg_rating=Avg("reviews__rating")).order_by("-avg_rating")[:3]
        return context

class RecipeView(FormMixin, DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"
    slug_field = "slug"
    form_class = ReviewForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user_review"] = self.object.get_user_review(self.request.user)
        context["reviews"] = self.object.reviews.all().order_by("-created_date")[:10]
        return context

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        if request.user == self.object.author:
            return HttpResponseForbidden()
        form = self.get_form()
        if form.is_valid():
            review = form.save(commit=False)
            review.recipe = self.object
            review.author = request.user
            review.save()
            return self.render_to_response(self.get_context_data(object=self.object))
        else:
            return self.form_invalid(form)


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

class ReviewDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = "recipes/review_delete.html"

    def get_success_url(self) -> str:
        return reverse("recipe-detail", kwargs={"slug": self.kwargs.get("slug")})
    
    def test_func(self) -> bool | None:
        review = self.get_object()
        return self.request.user.username == review.author.username
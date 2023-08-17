from typing import Any, Dict
from django.contrib import messages
from django.contrib.auth import login, get_user_model, logout
from django.http import Http404, HttpRequest, HttpResponse
from django.http.response import HttpResponse
from django.urls import reverse, reverse_lazy
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import CreateView, DetailView, ListView, UpdateView, FormView
from django.shortcuts import HttpResponseRedirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import CustomUserCreationForm, UserProfileImageForm, UserDeactivateForm
from recipes.models import Recipe


def redirect_to_users(request):
    return HttpResponseRedirect(reverse("users"))


class CreateUser(CreateView):
    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("users")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Registration successful")
        return HttpResponseRedirect(self.success_url)


class UserDetail(DetailView):
    model = get_user_model()
    template_name = "users/user_detail.html"
    context_object_name = "user_data"
    slug_field = "username"

    def get_object(self, queryset=None):
        object = super().get_object(queryset)
        if object.is_superuser is True or object.is_active is False:
            raise Http404
        return object


class UserList(ListView):
    model = get_user_model()
    template_name = "users/user_list.html"
    context_object_name = "users"
    paginate_by = 5

    def get_paginate_by(self, queryset):
        return self.request.GET.get("paginate_by", self.paginate_by)

    def get_queryset(self):
        queryset = (
            get_user_model()
            .objects.filter(is_superuser=False, is_staff=False, is_active=True)
            .order_by("-date_joined")
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        request.GET = request.GET.copy()
        request.GET["paginate_by"] = str(self.get_paginate_by(self.get_queryset()))
        return super().get(request, *args, **kwargs)


class UserProfileImageUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = get_user_model()
    form_class = UserProfileImageForm
    template_name = "users/profile_image_form.html"
    slug_field = "username"

    def get_success_url(self):
        success_url = reverse("user-detail", kwargs={"slug": self.object.username})
        return success_url

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            messages.error(self.request, form.errors["profile_image"][0])
            return self.form_invalid(form)

    def test_func(self):
        this_user = self.get_object()
        return self.request.user.username == this_user.username


class UserDeactivate(LoginRequiredMixin, UserPassesTestMixin, SingleObjectMixin, FormView):
    model = get_user_model()
    form_class = UserDeactivateForm
    success_url = reverse_lazy("users")
    template_name = "users/user_deactivate_form.html"
    slug_field = "username"

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        form = self.get_form()
        form.is_valid()
        if form.get_user() != self.get_object():
            form.invalidate_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form) -> HttpResponse:
        user = form.get_user()
        logout(self.request)
        user.is_active = False
        user.save()
        messages.success(self.request, "Account successfully deactivated.")
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        self.object = self.get_object()
        return super().get_context_data(**kwargs)

    def test_func(self):
        this_user = self.get_object()
        return self.request.user.username == this_user.username


class UserRecipeList(ListView):
    model = Recipe
    template_name = "users/user_recipe_list.html"
    user_context_object_name = "user_data"
    context_object_name = "recipes"
    slug_field = "username"
    paginate_by = 5


    def get_paginate_by(self, queryset):
        return self.request.GET.get("paginate_by", self.paginate_by)

    def get_queryset(self):
        queryset = self.object.recipes.all().order_by("-created_date")
        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context[self.user_context_object_name] = self.object
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        request.GET = request.GET.copy()
        request.GET["paginate_by"] = str(self.get_paginate_by(self.get_queryset()))
        return super().get(request, *args, **kwargs)

    def get_object(self):
        object = get_object_or_404(get_user_model(), username=self.kwargs.get("slug"))
        if object.is_superuser is True or object.is_active is False:
            raise Http404
        return object

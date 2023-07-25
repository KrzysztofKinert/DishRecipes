from typing import Any, Optional
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.db import models
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseNotFound
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from django.shortcuts import HttpResponseRedirect, render
from django.db.models.query import QuerySet

# Create your views here.

from .forms import CustomUserCreationForm


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

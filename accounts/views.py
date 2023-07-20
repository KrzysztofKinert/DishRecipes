from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.shortcuts import HttpResponseRedirect

# Create your views here.

from .forms import CustomUserCreationForm


class CreateUser(CreateView):
    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Registration successful")
        return HttpResponseRedirect(self.success_url)

from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("recipe/<str:slug>/", views.RecipeView.as_view(), name="recipe-detail"),
]

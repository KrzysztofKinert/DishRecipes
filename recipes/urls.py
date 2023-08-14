from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("recipes/", views.RecipeList.as_view(), name="recipe-list"),
    path("recipes/<str:slug>/", views.RecipeView.as_view(), name="recipe-detail"),
]

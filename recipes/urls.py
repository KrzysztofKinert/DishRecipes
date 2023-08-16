from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("recipes/", views.RecipeList.as_view(), name="recipe-list"),
    path("recipes/new/", views.RecipeCreate.as_view(), name="recipe-create"),
    path("recipes/recipe/<str:slug>/", views.RecipeView.as_view(), name="recipe-detail"),
    path("recipes/recipe/<str:slug>/update/", views.RecipeUpdate.as_view(), name="recipe-update"),
    path("recipes/recipe/<str:slug>/delete/", views.RecipeDelete.as_view(), name="recipe-delete"),
]

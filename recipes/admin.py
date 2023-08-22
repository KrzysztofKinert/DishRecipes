from django.contrib import admin

from .models import Recipe, Review

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ("title", "author", "created_date", "modified_date")
    list_display = ("title", "author", "created_date", "slug")
    readonly_fields = ["created_date", "modified_date", "slug",]

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_filter = ("author", "recipe", "created_date", "modified_date")
    list_display = ("author", "recipe", "created_date")
    readonly_fields = ["created_date", "modified_date"]
from django.contrib import admin

from .models import Recipe

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_filter = ("title", "author", "created_date", "modified_date")
    list_display = ("title", "author", "created_date", "slug")
    readonly_fields = ["created_date", "modified_date", "slug",]
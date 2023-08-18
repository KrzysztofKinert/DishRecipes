from django.forms import ModelForm, Textarea

from custom.widgets import widgets
from recipes.models import Recipe


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ("image", "title", "excerpt", "ingredients", "preparation", "serving")
        labels = {"image": ""}
        widgets = {
            "image": widgets.get("custom_clearable_image_input"),
            "excerpt": Textarea(),
            "ingredients": Textarea(),
            "preparation": Textarea(),
            "serving": Textarea(),
        }
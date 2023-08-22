from django.forms import ModelForm, Textarea, NumberInput

from custom.widgets import widgets
from recipes.models import Recipe, Review


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


class ReviewForm(ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "content")
        widgets = {
            "rating": NumberInput(
                attrs={
                    "min": "1",
                    "max": "5",
                }
            ),
            "content": Textarea(),
        }

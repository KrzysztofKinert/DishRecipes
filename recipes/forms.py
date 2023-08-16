from django.forms import ModelForm, Textarea

from recipes.models import Recipe


class RecipeForm(ModelForm):
    class Meta:
        model = Recipe
        fields = ("title", "excerpt", "ingredients", "preparation", "serving")
        widgets = {
            "excerpt": Textarea(),
            "ingredients": Textarea(),
            "preparation": Textarea(),
            "serving": Textarea(),
        }

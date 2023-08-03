from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.forms import ModelForm
from custom.widgets import widgets


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
        )


class UserProfileImageForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ("profile_image",)
        labels = {
            "profile_image": "",
        },
        widgets = {
            "profile_image": widgets.get("custom_clearable_image_input"),
        }

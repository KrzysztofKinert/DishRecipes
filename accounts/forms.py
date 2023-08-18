from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError as ValidationError
from django.forms import ModelForm, CharField, PasswordInput, Textarea
from django.utils.translation import gettext_lazy as _

from custom.widgets import widgets
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "username",
            "email",
        )


class UserProfileForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = ("profile_image", "profile_bio")
        labels = ({"profile_image": "", "profile_bio": "Your bio"},)
        widgets = {
            "profile_image": widgets.get("custom_clearable_image_input"),
            "profile_bio": Textarea(),
        }


class UserDeactivateForm(AuthenticationForm):
    password = CharField(
        label=_("Password"),
        strip=False,
        widget=PasswordInput(),
    )

    def invalidate_form(self):
        self.add_error(
            None,
            ValidationError(
                self.error_messages["invalid_login"],
                code="invalid_login",
                params={"username": self.username_field.verbose_name},
            ),
        )

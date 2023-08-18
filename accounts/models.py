from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator
from django.conf import settings


class CustomUserManager(UserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.EmailField(
        _("email address"),
        unique=True,
        max_length=320,
        help_text=_("Required."),
        validators=[EmailValidator(message="Invalid Email")],
        error_messages={
            "unique": _("A user with that email address already exists."),
        },
    )
    profile_image = models.ImageField(
        _("profile image"),
        max_length=200,
        upload_to="images",
        blank=True,
        default="images/default.jpg",
    )
    profile_bio = models.CharField(
        _("profile bio"),
        max_length=2000,
        blank=True,
    )

    objects = CustomUserManager()

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

    def profile_image_url_or_default(self):
        try:
            return self.profile_image.url
        except:
            return settings.MEDIA_URL + "images/default.jpg"

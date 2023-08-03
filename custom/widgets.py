from django.forms.widgets import ClearableFileInput


class CustomClearableImageInput(ClearableFileInput):
    template_name = "widgets/custom_clearable_image_input.html"


widgets = {
    "custom_clearable_image_input": CustomClearableImageInput,
}

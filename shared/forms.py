from django import forms


class DaisyUIFormMixin:
    """Base mixin to apply DaisyUI classes consistently across all forms"""

    WIDGET_CLASSES = {
        forms.TextInput: "input input-bordered w-full",
        forms.EmailInput: "input input-bordered w-full",
        forms.PasswordInput: "input input-bordered w-full",
        forms.URLInput: "input input-bordered w-full",
        forms.DateInput: "input input-bordered w-full",
        forms.NumberInput: "input input-bordered w-full",
        forms.Textarea: "textarea textarea-bordered w-full",
        forms.Select: "select select-bordered w-full",
        forms.CheckboxInput: "checkbox checkbox-primary",
        forms.FileInput: "file-input file-input-bordered w-full",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_daisy_ui_classes()

    def apply_daisy_ui_classes(self):
        """Apply DaisyUI classes to all form fields"""
        for field_name, field in self.fields.items():
            widget_class = type(field.widget)

            daisy_class = self.WIDGET_CLASSES.get(
                widget_class, "input input-bordered w-full"
            )

            existing_class = field.widget.attrs.get("class", "")
            if existing_class:
                field.widget.attrs["class"] = f"{existing_class} {daisy_class}"
            else:
                field.widget.attrs["class"] = daisy_class

            # Add focus states and transitions
            if widget_class != forms.CheckboxInput:
                field.widget.attrs["class"] += " focus:input-primary transition-all duration-200 placeholder:text-base-content/50"
            
            # Add better styling for specific field types
            if widget_class == forms.Select:
                field.widget.attrs["class"] += " focus:select-primary"
            elif widget_class == forms.Textarea:
                field.widget.attrs["class"] += " focus:textarea-primary resize-none"
                if "rows" not in field.widget.attrs:
                    field.widget.attrs["rows"] = "3"
            elif widget_class == forms.FileInput:
                field.widget.attrs["class"] += " focus:file-input-primary"


class FormHelper:
    """Helper class for consistent form rendering"""

    @staticmethod
    def get_field_wrapper_class():
        return "form-control w-full mb-4"

    @staticmethod
    def get_label_class():
        return "label"

    @staticmethod
    def get_label_text_class():
        return "label-text font-medium text-base-content"

    @staticmethod
    def get_help_text_class():
        return "label-text-alt text-base-content/70 mt-1"

    @staticmethod
    def get_error_class():
        return "label-text-alt text-error mt-1 font-medium"

    @staticmethod
    def get_button_class(variant="primary"):
        return f"btn btn-{variant} w-full mt-6 font-medium"

    @staticmethod
    def get_card_class():
        return ""  # No card wrapper in form template

    @staticmethod
    def get_card_body_class():
        return "space-y-1"

    @staticmethod
    def get_success_class():
        return "label-text-alt text-success mt-1"

    @staticmethod
    def get_loading_class():
        return "loading loading-spinner loading-sm"

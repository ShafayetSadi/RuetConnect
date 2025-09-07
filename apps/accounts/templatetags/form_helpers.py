from django import template
from shared.forms import FormHelper

register = template.Library()


@register.simple_tag
def form_helper():
    """Return FormHelper instance for use in templates"""
    return FormHelper()


@register.inclusion_tag("partials/_field.html")
def render_field(field, show_label=True):
    """Render a form field with consistent DaisyUI styling"""
    return {
        "field": field,
        "show_label": show_label,
        "helper": FormHelper,
    }

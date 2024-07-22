from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_rating(value):
    if value < 0 or value > 10:
        raise ValidationError(_(f'{value} is not between 0 and 10'), params={'value': value}, )

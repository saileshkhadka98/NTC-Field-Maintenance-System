from django.utils.dateparse import parse_date
from rest_framework.exceptions import ValidationError


def int_param(request, name):
    """Return the query parameter as an int, or None if absent."""
    raw = request.query_params.get(name)
    if raw in (None, ''):
        return None
    try:
        value = int(raw)
    except ValueError:
        raise ValidationError({name: 'Must be a whole number.'})
    if not 0 <= value <= 2_147_483_647:
        raise ValidationError({name: 'Value out of range.'})
    return value


def date_param(request, name):
    """Return the query parameter as a date (YYYY-MM-DD), or None if absent."""
    raw = request.query_params.get(name)
    if raw in (None, ''):
        return None
    try:
        parsed = parse_date(raw)
    except ValueError:
        parsed = None
    if parsed is None:
        raise ValidationError({name: 'Use the format YYYY-MM-DD.'})
    return parsed
import re
from django.forms import ValidationError


def alphanumeric(value):
    """Validate that name contains only alphabets and spaces"""
    if not value or not value.strip():
        raise ValidationError("Name cannot be blank.")
    if "  " in value:
        raise ValidationError("Name cannot have consecutive spaces.")
    if not re.match(r'^[a-zA-Z\s]+$', value):
        raise ValidationError("Name should only contain alphabets and spaces.")
    return value.strip()


def validate_Email(value):
    """Custom email validation"""
    if not value:
        raise ValidationError("Email cannot be blank.")

    value = value.strip().lower()

    if re.search(r'\s{2,}', value):
        raise ValidationError("Email should not contain consecutive spaces.")
    if re.search(r'\.\.', value):
        raise ValidationError("Email should not contain consecutive dots.")
    if '@' not in value:
        raise ValidationError("Email should contain '@' symbol.")
    if re.match(r'^\d', value):
        raise ValidationError("Email should not start with a number.")
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
        raise ValidationError("Please enter a valid email address.")
    return value


def validate_phone_number(value):
    """Validate Indian phone numbers"""
    if not value:
        raise ValidationError("Phone number cannot be blank.")

    cleaned = re.sub(r'\D', '', value)

    if not re.match(r'^[6-9]\d{9}$', cleaned):
        raise ValidationError("Phone number must start with 6, 7, 8, or 9 and be 10 digits long.")
    return cleaned

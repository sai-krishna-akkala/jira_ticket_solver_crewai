import re

def validate_phone(phone):
    pattern = r'^\+?\\d{10,15}$'
    return bool(re.match(pattern, phone))

def validate_form(data):
    # ...
    phone = data.get(\"phone\")
    if not phone or not validate_phone(phone):
        raise ValidationError(\"Invalid phone number\")
    # ...
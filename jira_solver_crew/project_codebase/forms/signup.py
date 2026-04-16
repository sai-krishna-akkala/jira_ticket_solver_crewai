"""
forms/signup.py — Signup form handler.
BUG: No phone number validation — accepts any string as a phone number.
"""


def validate_email(email):
    """Basic email validation."""
    if not email or "@" not in email:
        return False
    return True


def validate_form(data):
    """
    Validate signup form data.
    BUG: Does not validate phone number format — any string is accepted.
    """
    errors = []

    name = data.get("name", "").strip()
    if not name:
        errors.append("Name is required")

    email = data.get("email", "").strip()
    if not validate_email(email):
        errors.append("Invalid email address")

    password = data.get("password", "")
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")

    phone = data.get("phone", "").strip()
    if not phone:
        errors.append("Phone number is required")
    # BUG: No format validation — "not-a-phone" would pass

    if errors:
        return {"success": False, "errors": errors}

    return {
        "success": True,
        "user": {
            "name": name,
            "email": email,
            "phone": phone,
        },
    }


def signup(data):
    """Entry point for signup flow."""
    result = validate_form(data)
    return result

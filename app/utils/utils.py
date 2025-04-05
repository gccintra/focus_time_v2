import re

def validate_password(password):
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    if not re.search(r"[A-Za-z]", password):
        raise ValueError("The password must contain at least one letter.")

    if not re.search(r"\d", password):
        raise ValueError("The password must contain at least one number.")

    return True  # Senha válida
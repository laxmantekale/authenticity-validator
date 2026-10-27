import re

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone: str) -> bool:
    if not phone:
        return True
    pattern = r'^\+?[0-9]{7,15}$'
    return bool(re.match(pattern, phone.strip()))

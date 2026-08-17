import re


def password_es_segura(password):
    """
    Devuelve (True, None) si la contraseña cumple los requisitos,
    o (False, "mensaje de error") si no.
    Requisitos: mínimo 8 caracteres, al menos 1 mayúscula, al menos 1
    número, y al menos 1 carácter especial.
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe tener al menos una mayúscula."
    if not re.search(r"[0-9]", password):
        return False, "La contraseña debe tener al menos un número."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-]", password):
        return False, "La contraseña debe tener al menos un carácter especial (ej. !, @, #, .)."
    return True, None
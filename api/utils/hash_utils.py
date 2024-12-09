import bcrypt
import os
import base64


def hash_password(password: str):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt=salt)
    hashed_password = base64.b64encode(hashed_bytes).decode("utf-8")

    return hashed_password


def verify_password(plain_password: str, hashed_password: str):
    try:
        hashed_bytes = base64.b64decode(hashed_password.encode("utf-8"))
    except:
        return False

    try:
        pwd_bytes = plain_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)

    except ValueError:
        return False

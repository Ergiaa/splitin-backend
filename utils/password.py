from bcrypt import hashpw, checkpw, gensalt

def hash_password(plain: str) -> str:
    return hashpw(plain.encode(), gensalt())

def verify_password(plain: str, hashed: str) -> bool:
    return checkpw(plain.encode(), hashed.encode())
import jwt
from datetime import datetime, timedelta
from settings import SECRET_KEY

JWT_ALGORITHM = 'HS256'
EXPIRATION_HOURS = 2

def create_auth_token(user_id: str, type: str) -> str:
    return jwt.encode({
        "user_id": user_id,
        "user_type": type,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=EXPIRATION_HOURS)
    }, SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_auth_token(token: str) -> (dict, Exception):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=JWT_ALGORITHM), None
    except Exception as e:
        return None, e
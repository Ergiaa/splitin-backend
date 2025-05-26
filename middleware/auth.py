from functools import wraps
from flask import g as ctx, request, redirect, url_for

from utils.response import abort
from utils.jwt import decode_auth_token

def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.headers.get('Authorization')
        if not auth:
            return abort('Authorization header is required', 401)

        try:
            _, token = auth.split("Bearer ")
        except ValueError:
            return abort('Invalid Authorization header', 401)

        payload, error = decode_auth_token(token)
        if error:
            return abort('Invalid token', 401, error)

        ctx.user_id = payload['user_id']
        ctx.role = payload['user_type']

        return f(*args, **kwargs)
    return decorated_function
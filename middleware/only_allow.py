from functools import wraps
from flask import g as ctx, request, redirect, url_for

from utils.response import abort

def only_allow(roles: dict):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            for role in roles:
                if ctx.role == role:
                    return f(*args, **kwargs)

            return abort('role `{}` is not allowed'.format(ctx.role), 403)
        return decorated_function
    return decorator

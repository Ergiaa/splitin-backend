from flask_restful import Resource
from flask import g as ctx
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate

# Import your AuthService
from services import AuthService

auth_service = AuthService()

class AuthResource(Resource):
    def post(self):
        try:
            result = auth_service.login()
            return response("login success", 200, data=result)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 400)

    @authenticate
    def get(self):
        try:
            user_data = auth_service.me(ctx.user_id)
            return response("auth success", 200, data=user_data)
        except Exception as e:
            return abort(str(e), 404)

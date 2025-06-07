from flask_restful import Resource
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import UserService

user_service = UserService()

class UserResource(Resource):
    def post(self):
        try:
            user = user_service.create_user()
            return response("created successfully", 201, data=user)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 500, error=e)

    @authenticate
    def patch(self):
        try:
            updated_user = user_service.update_user()
            return response("updated successfully", 201, data=updated_user)
        except CustomError as e:
            return abort(e.message, e.status_code)
        except Exception as e:
            return abort(str(e), 500, error=e)

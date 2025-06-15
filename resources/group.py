from flask import request
from flask_restful import Resource
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import GroupService

group_service = GroupService()

class GroupResource(Resource):
    @authenticate
    def post(self):
        try:
          args = request.get_json()

          data = group_service.create_group(args)
          return response("created successfully", 201, data=data)
        except CustomError as e:
          return abort(e.message, e.status_code)
        except Exception as e:
          return abort(str(e), 500, error=e)

    @authenticate
    def get(self, group_id=None):
        try:
          if group_id is None:
            data = group_service.get_all_groups()
            return response("groups retrieved successfully", 200, data=data)
          if group_id is not None:
            data = group_service.get_group(group_id)
            return response("group retrieved successfully", 200, data=data)
        except CustomError as e:
          return abort(e.message, e.status_code)
        except Exception as e:
          return abort(str(e), 500, error=e)

    @authenticate
    def patch(self, group_id, user_id=None):
        try:
          data = group_service.join_group(group_id, user_id)
          return response("joined group successfully", 200, data=data)
        except CustomError as e:
          return abort(e.message, e.status_code)
        except Exception as e:
          return abort(str(e), 500, error=e)
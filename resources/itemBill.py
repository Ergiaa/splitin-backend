from flask import request
from flask_restful import Resource
from utils.response import response, abort
from utils.error import CustomError
from middleware.auth import authenticate
from services import BillService

bill_service = BillService()

class ItemBillResource(Resource):
    @authenticate
    def post(self, bill_id=None):
        try:
          args = request.get_json()

          data = bill_service.add_item(data=args, bill_id=bill_id)
          return response("added item successfully", 201, data=data)
        except CustomError as e:
          return abort(e.message, e.status_code)
        except Exception as e:
          return abort(str(e), 500, error=e)

    @authenticate
    def patch(self, bill_id=None):
        try:
          args = request.get_json()

          res = []

          for item in args:
            if not item.get("id"):
              return abort("item id is required", 400)

            if not item.get("assignments"):
              return abort("assignments are required", 400)

            if not isinstance(item.get("assignments"), list):
              return abort("assignments must be a list", 400)

            if len(item.get("assignments")) == 0:
              return abort("assignments cannot be empty", 400)

            if not all(isinstance(assignment, dict) for assignment in item.get("assignments")):
              return abort("each assignment must be a dictionary", 400)
          
          for item in args:
            res.append(bill_service.assign_items(bill_id=bill_id, item_id=item.get("id"), assignments=item.get("assignments", [])))
          return response("updated item successfully", 200, data=res)
        except CustomError as e:
          return abort(e.message, e.status_code)
        except Exception as e:
          return abort(str(e), 500, error=e)
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